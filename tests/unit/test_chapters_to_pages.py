from pathlib import Path

import pytest

from wllbe.generation.chapters_to_pages import generate_page_outline
from wllbe.generation.provider import FakeGenerationProvider


def test_generate_page_outline_returns_page_objects():
    provider = FakeGenerationProvider.from_file(Path("tests/fixtures/providers/page_outline.json"))
    approved_chapters = {"chapters": [{"chapter_id": "c1", "title": "Market problem"}]}
    result = generate_page_outline(approved_chapters, provider)

    assert result.pages[0].title == "The market is fragmented"
    assert result.pages[0].message == "Teams are stuck stitching together too many tools."
    assert result.pages[0].layout_hints == ["comparison"]
    assert provider.calls == [("chapters_to_pages", approved_chapters)]


def test_generate_page_outline_requires_fixture_response():
    provider = FakeGenerationProvider(responses={})

    with pytest.raises(ValueError, match="missing fixture response for task 'chapters_to_pages'"):
        generate_page_outline({}, provider)


def test_generate_page_outline_requires_pages_field():
    provider = FakeGenerationProvider(
        responses={
            "chapters_to_pages": {
                "chapters": [{"title": "x"}]
            }
        }
    )

    with pytest.raises(ValueError, match="missing required 'pages' field"):
        generate_page_outline({}, provider)


def test_generate_page_requires_page_objects():
    provider = FakeGenerationProvider(
        responses={
            "chapters_to_pages": {
                "pages": ["not an object"]
            }
        }
    )

    with pytest.raises(ValueError, match="page payload must be an object"):
        generate_page_outline({}, provider)


def test_generate_page_rejects_unknown_chapter_id():
    provider = FakeGenerationProvider(
        responses={
            "chapters_to_pages": {
                "pages": [
                    {
                        "page_id": "p1",
                        "chapter_id": "unknown",
                        "title": "Title",
                        "message": "Message",
                        "content_blocks": [],
                        "layout_hints": []
                    }
                ]
            }
        }
    )
    approved_chapters = {"chapters": [{"chapter_id": "c1", "title": "Market problem"}]}

    with pytest.raises(ValueError, match="page chapter_id 'unknown' is not in approved chapters"):
        generate_page_outline(approved_chapters, provider)


def test_generate_page_requires_all_required_fields():
    provider = FakeGenerationProvider(
        responses={
            "chapters_to_pages": {
                "pages": [
                    {
                        "page_id": "p1",
                        "chapter_id": "c1",
                        "title": "Title",
                        "content_blocks": [],
                        "layout_hints": []
                    }
                ]
            }
        }
    )
    approved_chapters = {"chapters": [{"chapter_id": "c1", "title": "Market problem"}]}

    with pytest.raises(ValueError, match="page payload missing required 'message' field"):
        generate_page_outline(approved_chapters, provider)


def test_generate_page_accepts_raw_text_and_validates_lists():
    provider = FakeGenerationProvider(
        responses={
            "chapters_to_pages": {
                "pages": [
                    {
                        "page_id": " p1 ",
                        "chapter_id": " c1 ",
                        "title": "Title\nwith whitespace",
                        "message": "  Message.  ",
                        "content_blocks": [],
                        "layout_hints": []
                    }
                ]
            }
        }
    )

    approved_chapters = {"chapters": [{"chapter_id": "c1", "title": "Market problem"}]}
    result = generate_page_outline(approved_chapters, provider)
    assert result.pages[0].page_id == "p1"
    assert result.pages[0].chapter_id == "c1"
    assert result.pages[0].content_blocks == []
    assert result.pages[0].layout_hints == []
