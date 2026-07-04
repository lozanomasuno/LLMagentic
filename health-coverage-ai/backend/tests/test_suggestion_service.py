import asyncio

from app.services.suggestion_service import SuggestionService


def test_suggestions_return_defaults_for_short_query():
    service = SuggestionService()
    result = asyncio.run(service.get_suggestions("re"))
    assert len(result) == 5


def test_suggestions_filter_by_query():
    service = SuggestionService()
    result = asyncio.run(service.get_suggestions("resonancia"))
    assert result
    assert any("resonancia" in item.lower() for item in result)
