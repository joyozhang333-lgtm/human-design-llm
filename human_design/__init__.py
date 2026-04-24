"""Human Design product workspace."""

from .bodygraph import render_bodygraph_svg, write_bodygraph_svg
from .career import generate_career_report, render_career_report_markdown
from .empirical import analyze_forced_choice_experiment
from .empirical_dataset import build_public_figure_manifest, load_manifest
from .prediction_registry import analyze_prospective_registry
from .engine import calculate_chart, parse_birth_datetime
from .input import normalize_birth_input, normalize_birth_time_range
from .product import build_llm_product
from .relationship import compare_relationship
from .relationship_product import build_relationship_product
from .relationship_reading import (
    generate_relationship_reading,
    render_relationship_reading_markdown,
)
from .reading import generate_reading, render_reading_markdown
from .timing import analyze_timing
from .timing_product import build_timing_product
from .timing_reading import generate_timing_reading, render_timing_reading_markdown
from .uncertainty import analyze_birth_time_range
from .version import VERSION as __version__

__all__ = [
    "__version__",
    "build_llm_product",
    "build_timing_product",
    "analyze_forced_choice_experiment",
    "analyze_prospective_registry",
    "build_public_figure_manifest",
    "load_manifest",
    "calculate_chart",
    "generate_career_report",
    "render_bodygraph_svg",
    "write_bodygraph_svg",
    "analyze_birth_time_range",
    "analyze_timing",
    "compare_relationship",
    "build_relationship_product",
    "normalize_birth_input",
    "normalize_birth_time_range",
    "parse_birth_datetime",
    "generate_reading",
    "render_career_report_markdown",
    "generate_timing_reading",
    "generate_relationship_reading",
    "render_reading_markdown",
    "render_timing_reading_markdown",
    "render_relationship_reading_markdown",
]
