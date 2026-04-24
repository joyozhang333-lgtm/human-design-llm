from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .schema import ChartInput, InputLocation

NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/search"
NOMINATIM_USER_AGENT = "human-design-llm/2.2 (+https://github.com/joyozhang333-lgtm/human-design-llm)"
TIMEAPI_ENDPOINT = "https://timeapi.io/api/TimeZone/coordinate"


class InputNormalizationError(ValueError):
    """Raised when birth input cannot be normalized safely."""


class LocationResolver(Protocol):
    def resolve(self, city: str, region: str | None, country: str | None) -> InputLocation:
        """Resolve a free-text location into coordinates and a display name."""


@dataclass(frozen=True)
class NormalizedBirthInput:
    birth_datetime_utc: datetime
    chart_input: ChartInput


@dataclass(frozen=True)
class NormalizedBirthRange:
    samples: tuple[NormalizedBirthInput, ...]
    interval_minutes: int


@dataclass(frozen=True)
class ResolvedTimezone:
    timezone_name: str
    source_precision: str
    warnings: tuple[str, ...]
    location: InputLocation | None


class NominatimLocationResolver:
    def resolve(self, city: str, region: str | None, country: str | None) -> InputLocation:
        query_parts = [city]
        if region:
            query_parts.append(region)
        if country:
            query_parts.append(country)
        query = ", ".join(query_parts)

        params = urlencode(
            {
                "q": query,
                "format": "jsonv2",
                "limit": 1,
            }
        )
        request = Request(
            f"{NOMINATIM_ENDPOINT}?{params}",
            headers={"User-Agent": NOMINATIM_USER_AGENT},
        )
        with urlopen(request, timeout=15) as response:
            payload = json.load(response)

        if not payload:
            raise InputNormalizationError(
                f"无法解析出生地点：{query}。请补充更完整的城市/地区/国家信息，或直接传入 --timezone。"
            )

        item = payload[0]
        latitude = float(item["lat"])
        longitude = float(item["lon"])

        return InputLocation(
            query=query,
            name=item.get("display_name", query),
            latitude=round(latitude, 6),
            longitude=round(longitude, 6),
        )


def parse_birth_datetime(raw: str) -> datetime:
    value = datetime.fromisoformat(raw)
    return normalize_datetime(value)


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def normalize_birth_input(
    birth_time: str | datetime,
    *,
    timezone_name: str | None = None,
    city: str | None = None,
    region: str | None = None,
    country: str | None = None,
    location_resolver: LocationResolver | None = None,
) -> NormalizedBirthInput:
    raw_birth_time, parsed_value = _coerce_birth_time(birth_time)

    resolved = _resolve_timezone(
        parsed_value,
        timezone_name=timezone_name,
        city=city,
        region=region,
        country=country,
        location_resolver=location_resolver,
    )
    localized = _localize_datetime(parsed_value, resolved.timezone_name)
    birth_datetime_utc = localized.astimezone(UTC)

    chart_input = ChartInput(
        raw_birth_time=raw_birth_time,
        birth_datetime_local=localized.isoformat(),
        timezone_name=resolved.timezone_name,
        source_precision=resolved.source_precision,
        warnings=resolved.warnings,
        location=resolved.location,
    )
    return NormalizedBirthInput(
        birth_datetime_utc=birth_datetime_utc,
        chart_input=chart_input,
    )


def normalize_birth_time_range(
    start_birth_time: str | datetime,
    end_birth_time: str | datetime,
    *,
    timezone_name: str | None = None,
    city: str | None = None,
    region: str | None = None,
    country: str | None = None,
    interval_minutes: int = 30,
    location_resolver: LocationResolver | None = None,
) -> NormalizedBirthRange:
    if interval_minutes <= 0:
        raise InputNormalizationError("区间采样间隔必须大于 0 分钟。")

    _, start_value = _coerce_birth_time(start_birth_time)
    _, end_value = _coerce_birth_time(end_birth_time)
    _validate_range_endpoints(start_value, end_value)

    resolved = _resolve_timezone(
        start_value,
        timezone_name=timezone_name,
        city=city,
        region=region,
        country=country,
        location_resolver=location_resolver,
    )

    localized_start = _localize_datetime(start_value, resolved.timezone_name)
    localized_end = _localize_datetime(end_value, resolved.timezone_name)
    if localized_end < localized_start:
        raise InputNormalizationError("出生时间区间的结束时间不能早于开始时间。")

    samples = tuple(
        _build_normalized_sample(sample_time, resolved)
        for sample_time in _iterate_range_samples(
            localized_start,
            localized_end,
            interval_minutes=interval_minutes,
        )
    )
    return NormalizedBirthRange(samples=samples, interval_minutes=interval_minutes)


def _coerce_birth_time(value: str | datetime) -> tuple[str, datetime]:
    if isinstance(value, datetime):
        raw = value.isoformat()
        return raw, value
    return value, datetime.fromisoformat(value)


def _build_normalized_sample(
    localized: datetime,
    resolved: ResolvedTimezone,
) -> NormalizedBirthInput:
    birth_datetime_utc = localized.astimezone(UTC)
    chart_input = ChartInput(
        raw_birth_time=localized.isoformat(),
        birth_datetime_local=localized.isoformat(),
        timezone_name=resolved.timezone_name,
        source_precision=resolved.source_precision,
        warnings=resolved.warnings,
        location=resolved.location,
    )
    return NormalizedBirthInput(
        birth_datetime_utc=birth_datetime_utc,
        chart_input=chart_input,
    )


def _validate_range_endpoints(start_value: datetime, end_value: datetime) -> None:
    if (start_value.tzinfo is None) != (end_value.tzinfo is None):
        raise InputNormalizationError(
            "区间开始和结束时间必须同时带时区，或同时不带时区。"
        )
    if start_value.tzinfo is not None and end_value.tzinfo is not None:
        start_offset = start_value.utcoffset()
        end_offset = end_value.utcoffset()
        if start_offset != end_offset:
            raise InputNormalizationError(
                "带显式 offset 的区间开始和结束时间当前必须使用同一个 offset；若跨 DST，改用无 offset 时间并配合 --timezone。"
            )


def _iterate_range_samples(
    start_value: datetime,
    end_value: datetime,
    *,
    interval_minutes: int,
) -> tuple[datetime, ...]:
    step = timedelta(minutes=interval_minutes)
    current = start_value
    samples: list[datetime] = []
    while current <= end_value:
        samples.append(current)
        current += step
    if samples[-1] != end_value:
        samples.append(end_value)
    return tuple(samples)


def _resolve_timezone(
    birth_time: datetime,
    *,
    timezone_name: str | None,
    city: str | None,
    region: str | None,
    country: str | None,
    location_resolver: LocationResolver | None,
) -> ResolvedTimezone:
    warnings: list[str] = []
    location_parts = [city, region, country]
    has_location_hint = any(location_parts)

    if birth_time.tzinfo is not None:
        if timezone_name or has_location_hint:
            warnings.append("出生时间已包含 UTC offset，额外的地点或时区提示未参与计算。")
        tz_name = _tz_display_name(birth_time)
        return ResolvedTimezone(
            timezone_name=tz_name,
            source_precision="explicit-offset",
            warnings=tuple(warnings),
            location=None,
        )

    if timezone_name:
        _load_zoneinfo(timezone_name)
        if has_location_hint:
            warnings.append("已优先使用明确传入的 timezone，地点信息仅保留为参考。")
        return ResolvedTimezone(
            timezone_name=timezone_name,
            source_precision="timezone-name",
            warnings=tuple(warnings),
            location=None,
        )

    if has_location_hint:
        if not city:
            raise InputNormalizationError("使用地点解析时区时，至少需要提供 --city。")
        resolver = _coerce_location_resolver(location_resolver)
        location = resolver.resolve(city=city, region=region, country=country)
        resolved_timezone_name = _resolve_timezone_from_coordinates(location)
        if not country:
            warnings.append("地点解析未提供国家信息，结果可能存在歧义。")
        warnings.append("当前 UTC 时间来自地点推断出的 IANA 时区；夏令时和历史时区规则已按该时区计算。")
        return ResolvedTimezone(
            timezone_name=resolved_timezone_name,
            source_precision="city-resolved",
            warnings=tuple(warnings),
            location=location,
        )

    warnings.append("出生时间未提供时区，当前按 UTC 处理；这会影响人类图结果精度。")
    return ResolvedTimezone(
        timezone_name="UTC",
        source_precision="assumed-utc",
        warnings=tuple(warnings),
        location=None,
    )


def _coerce_location_resolver(
    location_resolver: LocationResolver | None,
) -> LocationResolver:
    if location_resolver is not None:
        return location_resolver
    return NominatimLocationResolver()


def _resolve_timezone_from_coordinates(location: InputLocation) -> str:
    params = urlencode(
        {
            "latitude": location.latitude,
            "longitude": location.longitude,
        }
    )
    request = Request(
        f"{TIMEAPI_ENDPOINT}?{params}",
        headers={"User-Agent": NOMINATIM_USER_AGENT},
    )
    with urlopen(request, timeout=15) as response:
        payload = json.load(response)
    timezone_name = payload.get("timeZone")
    if not timezone_name:
        raise InputNormalizationError(
            f"地点已解析，但无法确定时区：{location.query}。请改用 --timezone 明确指定 IANA 时区。"
        )
    return timezone_name


def _localize_datetime(value: datetime, timezone_name: str) -> datetime:
    if value.tzinfo is not None:
        return value
    return value.replace(tzinfo=_load_zoneinfo(timezone_name))


def _load_zoneinfo(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise InputNormalizationError(
            f"无法识别时区：{timezone_name}。请传入合法的 IANA 时区，例如 Asia/Shanghai。"
        ) from exc


def _tz_display_name(value: datetime) -> str:
    tzinfo = value.tzinfo
    if tzinfo is None:
        return "UTC"
    zone_key = getattr(tzinfo, "key", None)
    if zone_key:
        return zone_key
    name = value.tzname()
    if name:
        return name
    return "UTC"
