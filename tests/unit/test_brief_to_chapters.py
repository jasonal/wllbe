from pathlib import Path

from wllbe.generation.brief_to_chapters import generate_chapter_outline
from wllbe.generation.provider import FakeGenerationProvider


def test_generate_chapter_outline_returns_structured_chapters():
    provider = FakeGenerationProvider.from_file(Path("tests/fixtures/providers/chapter_outline.json"))
    result = generate_chapter_outline("launch a new AI product", provider)

    assert result.goal == "Launch the new AI product to market leaders."
    assert result.audience == "Senior Product and GTM leaders"
    assert result.tone == "Crisp, confident, and practical"
    assert result.chapters[0].title == "Why this launch matters"
    assert result.chapters[0].estimated_pages == 2
    assert result.chapters[0].estimated_pages != " 2 pages "
