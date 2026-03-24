import requests

OFF_BASE = "https://world.openfoodfacts.org"
HEADERS = {"User-Agent": "InventoryManagementSystem/1.0"}


def _normalize(product):
    return {
        "barcode": product.get("code", ""),
        "product_name": product.get("product_name_en") or product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "category": (product.get("categories", "") or "").split(",")[0].strip(),
        "ingredients_text": product.get("ingredients_text_en") or product.get("ingredients_text", ""),
        "quantity": product.get("quantity", ""),
        "nutriscore_grade": product.get("nutriscore_grade"),
    }


def fetch_by_barcode(barcode):
    url = f"{OFF_BASE}/api/v2/product/{barcode}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != 1:
            return None
        return _normalize(data["product"])
    except requests.RequestException:
        return None


def fetch_by_name(name):
    url = f"{OFF_BASE}/cgi/search.pl"
    params = {
        "search_terms": name,
        "json": 1,
        "page_size": 5,
        "fields": "code,product_name,product_name_en,brands,categories,ingredients_text,ingredients_text_en,quantity,nutriscore_grade",
    }
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])
        return [_normalize(p) for p in products]
    except requests.RequestException:
        return []
