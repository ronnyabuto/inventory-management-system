inventory = [
    {
        "id": 1,
        "barcode": "3017620422003",
        "product_name": "Nutella",
        "brand": "Ferrero",
        "category": "Spreads",
        "ingredients_text": "Sugar, palm oil, hazelnuts 13%, low-fat cocoa 7.4%, skimmed milk powder 6.6%, whey powder, emulsifiers: lecithins [soya], vanillin",
        "price": 4.99,
        "stock_quantity": 120,
        "unit": "400g",
    },
    {
        "id": 2,
        "barcode": "7613034626844",
        "product_name": "Nescafe Classic",
        "brand": "Nescafe",
        "category": "Beverages",
        "ingredients_text": "100% pure soluble coffee",
        "price": 6.49,
        "stock_quantity": 85,
        "unit": "200g",
    },
    {
        "id": 3,
        "barcode": "8076809513388",
        "product_name": "Barilla Spaghetti",
        "brand": "Barilla",
        "category": "Pasta",
        "ingredients_text": "Durum wheat semolina, water",
        "price": 1.79,
        "stock_quantity": 300,
        "unit": "500g",
    },
    {
        "id": 4,
        "barcode": "5000159407236",
        "product_name": "Heinz Baked Beans",
        "brand": "Heinz",
        "category": "Canned Goods",
        "ingredients_text": "Beans (51%), tomatoes (34%), water, sugar, modified cornflour, salt, spirit vinegar, spice extracts, herb extract",
        "price": 0.89,
        "stock_quantity": 450,
        "unit": "415g",
    },
    {
        "id": 5,
        "barcode": "0038000138416",
        "product_name": "Kellogg's Corn Flakes",
        "brand": "Kellogg's",
        "category": "Cereals",
        "ingredients_text": "Milled corn, sugar, salt, high fructose corn syrup, malt flavoring",
        "price": 3.25,
        "stock_quantity": 200,
        "unit": "500g",
    },
    {
        "id": 6,
        "barcode": "3041090108028",
        "product_name": "Evian Natural Spring Water",
        "brand": "Evian",
        "category": "Beverages",
        "ingredients_text": "Natural mineral water",
        "price": 1.20,
        "stock_quantity": 600,
        "unit": "1.5L",
    },
    {
        "id": 7,
        "barcode": "5000113100215",
        "product_name": "Cadbury Dairy Milk",
        "brand": "Cadbury",
        "category": "Confectionery",
        "ingredients_text": "Milk, sugar, cocoa butter, cocoa mass, vegetable fats, emulsifiers, flavourings",
        "price": 1.50,
        "stock_quantity": 180,
        "unit": "200g",
    },
    {
        "id": 8,
        "barcode": "4005808729203",
        "product_name": "Nivea Soft Moisturising Cream",
        "brand": "Nivea",
        "category": "Personal Care",
        "ingredients_text": "Water, glycerin, mineral oil, isohexadecane, jojoba oil",
        "price": 3.99,
        "stock_quantity": 95,
        "unit": "200ml",
    },
]

_next_id = 9


def get_all():
    return inventory


def get_by_id(item_id):
    return next((item for item in inventory if item["id"] == item_id), None)


def add(item):
    global _next_id
    item["id"] = _next_id
    _next_id += 1
    inventory.append(item)
    return item


def update(item_id, data):
    item = get_by_id(item_id)
    if item is None:
        return None
    for key, value in data.items():
        if key != "id":
            item[key] = value
    return item


def remove(item_id):
    item = get_by_id(item_id)
    if item is None:
        return False
    inventory.remove(item)
    return True


def next_id():
    return _next_id
