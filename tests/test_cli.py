from unittest.mock import MagicMock, patch

import requests as req_lib

import cli

SAMPLE_ITEM = {
    "id": 1,
    "product_name": "Nutella",
    "brand": "Ferrero",
    "category": "Spreads",
    "barcode": "3017620422003",
    "price": 4.99,
    "stock_quantity": 120,
    "unit": "400g",
    "ingredients_text": "Sugar, palm oil, hazelnuts",
}

SAMPLE_PRODUCT = {
    "product_name": "Nutella",
    "brand": "Ferrero",
    "barcode": "3017620422003",
    "category": "Spreads",
    "quantity": "400g",
    "nutriscore_grade": "e",
    "ingredients_text": "Sugar, palm oil, hazelnuts",
}


def make_response(status_code=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    if status_code >= 400:
        mock.raise_for_status.side_effect = req_lib.HTTPError(f"HTTP {status_code}")
    else:
        mock.raise_for_status.return_value = None
    return mock


# --- list_inventory ---

@patch("cli.requests.get")
def test_list_inventory_success(mock_get):
    mock_get.return_value = make_response(200, [SAMPLE_ITEM])
    cli.list_inventory()
    mock_get.assert_called_once_with("http://localhost:5000/inventory")


@patch("cli.requests.get")
def test_list_inventory_empty(mock_get):
    mock_get.return_value = make_response(200, [])
    cli.list_inventory()
    mock_get.assert_called_once()


@patch("cli.requests.get")
def test_list_inventory_connection_error(mock_get):
    mock_get.side_effect = req_lib.ConnectionError
    cli.list_inventory()


# --- view_item ---

@patch("cli.requests.get")
@patch("builtins.input", return_value="1")
def test_view_item_success(mock_input, mock_get):
    mock_get.return_value = make_response(200, SAMPLE_ITEM)
    cli.view_item()
    mock_get.assert_called_once_with("http://localhost:5000/inventory/1")


@patch("cli.requests.get")
@patch("builtins.input", return_value="999")
def test_view_item_not_found(mock_input, mock_get):
    mock_get.return_value = make_response(404, {"error": "not found"})
    cli.view_item()
    mock_get.assert_called_once()


@patch("builtins.input", return_value="abc")
def test_view_item_invalid_id(mock_input):
    cli.view_item()


# --- add_item ---

@patch("cli.requests.post")
@patch("builtins.input", side_effect=["Test Product", "Brand", "Cat", "123", "500g", "ingredients", "2.99", "10"])
def test_add_item_success(mock_input, mock_post):
    mock_post.return_value = make_response(201, SAMPLE_ITEM)
    cli.add_item()
    mock_post.assert_called_once()
    payload = mock_post.call_args[1]["json"]
    assert payload["product_name"] == "Test Product"
    assert payload["price"] == 2.99
    assert payload["stock_quantity"] == 10


@patch("builtins.input", return_value="")
def test_add_item_missing_name(mock_input):
    cli.add_item()


@patch("builtins.input", side_effect=["Product", "Brand", "Cat", "123", "500g", "ingredients", "notaprice", "10"])
def test_add_item_invalid_price(mock_input):
    cli.add_item()


# --- update_item ---

@patch("cli.requests.patch")
@patch("builtins.input", side_effect=["1", "1", "5.99"])
def test_update_item_price(mock_input, mock_patch):
    mock_patch.return_value = make_response(200, {**SAMPLE_ITEM, "price": 5.99})
    cli.update_item()
    mock_patch.assert_called_once()
    assert mock_patch.call_args[1]["json"]["price"] == 5.99


@patch("cli.requests.patch")
@patch("builtins.input", side_effect=["1", "2", "200"])
def test_update_item_stock(mock_input, mock_patch):
    mock_patch.return_value = make_response(200, {**SAMPLE_ITEM, "stock_quantity": 200})
    cli.update_item()
    mock_patch.assert_called_once()
    assert mock_patch.call_args[1]["json"]["stock_quantity"] == 200


@patch("cli.requests.patch")
@patch("builtins.input", side_effect=["1", "3", "9.99", "50"])
def test_update_item_both(mock_input, mock_patch):
    mock_patch.return_value = make_response(200, {**SAMPLE_ITEM, "price": 9.99, "stock_quantity": 50})
    cli.update_item()
    mock_patch.assert_called_once()
    payload = mock_patch.call_args[1]["json"]
    assert payload["price"] == 9.99
    assert payload["stock_quantity"] == 50


@patch("cli.requests.patch")
@patch("builtins.input", side_effect=["999", "1", "5.99"])
def test_update_item_not_found(mock_input, mock_patch):
    mock_patch.return_value = make_response(404, {"error": "not found"})
    cli.update_item()
    mock_patch.assert_called_once()


# --- delete_item ---

@patch("cli.requests.delete")
@patch("builtins.input", side_effect=["1", "y"])
def test_delete_item_confirmed(mock_input, mock_delete):
    mock_delete.return_value = make_response(204)
    cli.delete_item()
    mock_delete.assert_called_once_with("http://localhost:5000/inventory/1")


@patch("cli.requests.delete")
@patch("builtins.input", side_effect=["1", "n"])
def test_delete_item_cancelled(mock_input, mock_delete):
    cli.delete_item()
    mock_delete.assert_not_called()


@patch("cli.requests.delete")
@patch("builtins.input", side_effect=["999", "y"])
def test_delete_item_not_found(mock_input, mock_delete):
    mock_delete.return_value = make_response(404, {"error": "not found"})
    cli.delete_item()
    mock_delete.assert_called_once()


# --- lookup_product ---

@patch("cli.requests.get")
@patch("builtins.input", side_effect=["1", "3017620422003", "n"])
def test_lookup_by_barcode_found_skip_add(mock_input, mock_get):
    mock_get.return_value = make_response(200, SAMPLE_PRODUCT)
    cli.lookup_product()
    mock_get.assert_called_once()


@patch("cli.requests.post")
@patch("cli.requests.get")
@patch("builtins.input", side_effect=["1", "3017620422003", "y", "4.99", "100"])
def test_lookup_by_barcode_and_add(mock_input, mock_get, mock_post):
    mock_get.return_value = make_response(200, SAMPLE_PRODUCT)
    mock_post.return_value = make_response(201, SAMPLE_ITEM)
    cli.lookup_product()
    mock_post.assert_called_once()
    payload = mock_post.call_args[1]["json"]
    assert payload["product_name"] == "Nutella"
    assert payload["price"] == 4.99
    assert payload["stock_quantity"] == 100


@patch("cli.requests.get")
@patch("builtins.input", side_effect=["1", "0000000000000"])
def test_lookup_by_barcode_not_found(mock_input, mock_get):
    mock_get.return_value = make_response(404, {"error": "not found"})
    cli.lookup_product()
    mock_get.assert_called_once()


@patch("cli.requests.get")
@patch("builtins.input", side_effect=["2", "Nutella", "0"])
def test_lookup_by_name_skip_add(mock_input, mock_get):
    mock_get.return_value = make_response(200, [SAMPLE_PRODUCT])
    cli.lookup_product()
    mock_get.assert_called_once()


@patch("cli.requests.post")
@patch("cli.requests.get")
@patch("builtins.input", side_effect=["2", "Nutella", "1", "y", "4.99", "100"])
def test_lookup_by_name_and_add(mock_input, mock_get, mock_post):
    mock_get.return_value = make_response(200, [SAMPLE_PRODUCT])
    mock_post.return_value = make_response(201, SAMPLE_ITEM)
    cli.lookup_product()
    mock_post.assert_called_once()
    payload = mock_post.call_args[1]["json"]
    assert payload["product_name"] == "Nutella"
    assert payload["price"] == 4.99


@patch("cli.requests.get")
@patch("builtins.input", side_effect=["2", "xyznotaproduct", "0"])
def test_lookup_by_name_empty_results(mock_input, mock_get):
    mock_get.return_value = make_response(200, [])
    cli.lookup_product()
    mock_get.assert_called_once()


@patch("builtins.input", return_value="9")
def test_lookup_invalid_choice(mock_input):
    cli.lookup_product()
