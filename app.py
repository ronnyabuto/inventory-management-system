from flask import Flask, jsonify, request

import database
from external_api import fetch_by_barcode, fetch_by_name

app = Flask(__name__)

REQUIRED_FIELDS = {"product_name", "price", "stock_quantity"}


def _item_not_found(item_id):
    return jsonify({"error": f"Item with id {item_id} not found"}), 404


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(database.get_all()), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = database.get_by_id(item_id)
    if item is None:
        return _item_not_found(item_id)
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def create_item():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        return jsonify({"error": f"Missing required fields: {sorted(missing)}"}), 400
    item = {
        "barcode": data.get("barcode", ""),
        "product_name": data["product_name"],
        "brand": data.get("brand", ""),
        "category": data.get("category", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "price": float(data["price"]),
        "stock_quantity": int(data["stock_quantity"]),
        "unit": data.get("unit", ""),
    }
    new_item = database.add(item)
    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    updated = database.update(item_id, data)
    if updated is None:
        return _item_not_found(item_id)
    return jsonify(updated), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    removed = database.remove(item_id)
    if not removed:
        return _item_not_found(item_id)
    return "", 204


@app.route("/inventory/lookup", methods=["GET"])
def lookup_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")
    if not barcode and not name:
        return jsonify({"error": "Provide a 'barcode' or 'name' query parameter"}), 400
    if barcode:
        result = fetch_by_barcode(barcode)
        if result is None:
            return jsonify({"error": f"No product found for barcode: {barcode}"}), 404
        return jsonify(result), 200
    results = fetch_by_name(name)
    return jsonify(results), 200


if __name__ == "__main__":
    app.run(debug=True)
