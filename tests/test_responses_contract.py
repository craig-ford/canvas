import re
from datetime import datetime
from canvas import success_response, list_response


def test_success_response_structure():
    """Test success_response returns correct envelope format"""
    data = {"test": "value"}
    result = success_response(data)
    
    assert "data" in result
    assert "meta" in result
    assert result["data"] == data
    assert "timestamp" in result["meta"]


def test_list_response_structure():
    """Test list_response returns correct pagination format"""
    data = [{"item": 1}, {"item": 2}]
    total = 10
    result = list_response(data, total, page=2, per_page=5)
    
    assert "data" in result
    assert "meta" in result
    assert result["data"] == data
    assert result["meta"]["total"] == total
    assert result["meta"]["page"] == 2
    assert result["meta"]["per_page"] == 5
    assert "timestamp" in result["meta"]


def test_response_timestamp_format():
    """Test timestamp format is ISO 8601 with timezone"""
    result = success_response({"test": "data"})
    timestamp = result["meta"]["timestamp"]
    
    # ISO 8601 format with timezone: YYYY-MM-DDTHH:MM:SS.fffffZ or +HH:MM
    iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$'
    assert re.match(iso_pattern, timestamp)
    
    # Should be parseable as datetime
    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))