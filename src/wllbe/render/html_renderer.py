from __future__ import annotations

from pathlib import Path
from typing import Any

TEMPLATES_DIR = Path(__file__).parent / "templates"
DECK_TEMPLATE = (TEMPLATES_DIR / "deck.html").read_text()
SLIDE_TEMPLATE = (TEMPLATES_DIR / "slide.html").read_text()
THEME_TEMPLATE = (TEMPLATES_DIR / "theme.css").read_text()

RenderedSlide = dict[str, Any]


def render_version(version_id: str, slides: list[RenderedSlide], style_pack: dict[str, Any]) -> str:
    """Compose a single HTML document for a given version."""
    slide_html = "\n".join(render_slide(slide) for slide in slides)
    theme_css = render_theme_css(style_pack)
    return DECK_TEMPLATE.format(
        version_id=version_id,
        slide_html=slide_html,
        theme_css=theme_css,
    )


def render_slide(slide: RenderedSlide) -> str:
    """Render one slide using the slide template."""
    return SLIDE_TEMPLATE.format(
        slide_id=slide.get("slide_id", ""),
        title=slide.get("title", ""),
        body_html=slide.get("body_html", ""),
    )


def render_theme_css(style_pack: dict[str, Any]) -> str:
    """Fill theme CSS with tokens from the style pack."""
    tokens = style_pack.get("tokens", {})
    bg = tokens.get("bg", tokens.get("background", ""))
    text = tokens.get("text", tokens.get("foreground", ""))
    return THEME_TEMPLATE.format(
        bg=bg,
        text=text,
    )
