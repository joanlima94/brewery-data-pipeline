import pytest
import responses
from etl.src.api_to_bronze import get_total_breweries, get_breweries_page

API_BASE_URL = "https://api.openbrewerydb.org/v1"

@responses.activate
def test_get_total_breweries_success():
    """Test metadata endpoint call."""
    mock_response = {"total": 8372}
    responses.add(
        responses.GET,
        f"{API_BASE_URL}/breweries/meta",
        json=mock_response,
        status=200
    )

    total = get_total_breweries()
    assert total == 8372


@responses.activate
def test_get_breweries_page_success():
    """Test brewery page endpoint call."""
    mock_page = [
        {
            "id": "madtree-brewing-cincinnati",
            "name": "MadTree Brewing",
            "brewery_type": "regional",
            "street": "3301 Madison Rd",
            "city": "Cincinnati",
            "state": "Ohio",
            "postal_code": "45209-1132",
            "country": "United States",
            "longitude": "-84.4239715",
            "latitude": "39.1543684",
            "phone": "5138368733",
            "website_url": "http://www.madtreebrewing.com"
        }
    ]
    responses.add(
        responses.GET,
        f"{API_BASE_URL}/breweries?page=1&per_page=200",
        json=mock_page,
        status=200
    )

    result = get_breweries_page(1)
    assert len(result) == 1
    assert result[0]["name"] == "MadTree Brewing"

@pytest.mark.integration
def test_real_api_connection():
    total = get_total_breweries()
    assert total > 0