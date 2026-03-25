from pathlib import Path

import pytest

from wllbe.generation.brief_to_chapters import generate_chapter_outline
from wllbe.generation.provider import FakeGenerationProvider


def test_generate_chapter_outline_returns_structured_chapters():
    raw_brief = Path("tests/fixtures/briefs/product-launch.md").read_text(encoding="utf-8")
    provider = FakeGenerationProvider.from_file(Path("tests/fixtures/providers/chapter_outline.json"))
    result = generate_chapter_outline(raw_brief, provider)

    assert result.goal == "Launch the new AI product to market leaders."
    assert result.audience == "Senior Product and GTM leaders"
    assert result.tone == "Crisp, confident, and practical"
    assert result.chapters[0].title == "Why this launch matters"
    assert result.chapters[0].estimated_pages == 2
    assert result.chapters[0].estimated_pages != " 2 pages "
    assert provider.calls == [("brief_to_chapters", {"brief": raw_brief})]


def test_generate_chapter_outline_requires_fixture_for_requested_task():
    provider = FakeGenerationProvider(responses={})

    with pytest.raises(ValueError, match="missing fixture response for task 'brief_to_chapters'"):
        generate_chapter_outline("brief text", provider)


def test_generate_chapter_outline_requires_chapters_field():
    provider = FakeGenerationProvider(
        responses={
            "brief_to_chapters": {
                "goal": "Goal",
                "audience": "Audience",
                "tone": "Tone",
            }
        }
    )

    with pytest.raises(ValueError, match="missing required 'chapters' field"):
        generate_chapter_outline("brief text", provider)
