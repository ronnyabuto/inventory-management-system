from unittest.mock import MagicMock, patch

import pytest
import requests as req_lib

from external_api import fetch_by_barcode, fetch_by_name

MOCK_PRODUCT = {
    "code": "3017620422003",
    "product_name_en": "Nutella",
    "brands": "Ferrero",
    "categories": "Spreads, Sweet spreads",
    "ingredients_text_en": "Sugar, palm oil, hazelnuts 13%, low-fat cocoa 7.4%",
    "quantity": "400 g",
    "nutriscore_grade": "e",
}

MOCK_OFF_BARCODE_RESPONSE = {"status": 1, "product": MOCK_PRODUCT}
MOCK_OFF_SEARCH_RESPONSE = {"products": [MOCK_PRODUCT]}
MOCK_OFF_NOT_FOUND = {"status": 0}


@patch("external_api.requests.get")
def test_fetch_by_barcode_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_OFF_BARCODE_RESPONSE
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = fetch_by_barcode("3017620422003")

    assert result is not None
    assert result["barcode"] == "3017620422003"
    assert result["product_name"] == "Nutella"
    assert result["brand"] == "Ferrero"
    assert result["nutriscore_grade"] == "e"
    assert "quantity" in result
    assert "ingredients_text" in result


@patch("external_api.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_OFF_NOT_FOUND
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = fetch_by_barcode("0000000000000")

    assert result is None


@patch("external_api.requests.get")
def test_fetch_by_barcode_network_error(mock_get):
    mock_get.side_effect = req_lib.RequestException("Connection refused")

    result = fetch_by_barcode("3017620422003")

    assert result is None


@patch("external_api.requests.get")
def test_fetch_by_name_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_OFF_SEARCH_RESPONSE
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    results = fetch_by_name("Nutella")

    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["product_name"] == "Nutella"


@patch("external_api.requests.get")
def test_fetch_by_name_empty_results(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"products": []}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    results = fetch_by_name("xyznonexistentproduct")

    assert results == []


@patch("external_api.requests.get")
def test_fetch_by_name_network_error(mock_get):
    mock_get.side_effect = req_lib.RequestException("Timeout")

    results = fetch_by_name("Nutella")

    assert results == []
