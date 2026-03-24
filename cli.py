import sys

import requests

BASE_URL = "http://localhost:5000"


def print_item(item):
    print(f"\n  ID:           {item.get('id')}")
    print(f"  Product:      {item.get('product_name')}")
    print(f"  Brand:        {item.get('brand')}")
    print(f"  Category:     {item.get('category')}")
    print(f"  Barcode:      {item.get('barcode')}")
    print(f"  Price:        ${item.get('price'):.2f}")
    print(f"  Stock:        {item.get('stock_quantity')} x {item.get('unit')}")
    print(f"  Ingredients:  {item.get('ingredients_text', '')[:80]}...")


def print_off_product(product):
    print(f"\n  Product:     {product.get('product_name')}")
    print(f"  Brand:       {product.get('brand')}")
    print(f"  Barcode:     {product.get('barcode')}")
    print(f"  Category:    {product.get('category')}")
    print(f"  Quantity:    {product.get('quantity')}")
    print(f"  Nutriscore:  {product.get('nutriscore_grade', 'N/A')}")
    print(f"  Ingredients: {(product.get('ingredients_text') or '')[:80]}...")


def list_inventory():
    try:
        r = requests.get(f"{BASE_URL}/inventory")
        r.raise_for_status()
        items = r.json()
        if not items:
            print("Inventory is empty.")
            return
        print(f"\n{'='*60}")
        print(f"  INVENTORY ({len(items)} items)")
        print(f"{'='*60}")
        for item in items:
            print_item(item)
            print()
    except requests.ConnectionError:
        print("Error: Cannot connect to the API server. Is it running?")
    except requests.HTTPError as e:
        print(f"Error: {e}")


def view_item():
    item_id = input("Enter item ID: ").strip()
    if not item_id.isdigit():
        print("Invalid ID.")
        return
    try:
        r = requests.get(f"{BASE_URL}/inventory/{item_id}")
        if r.status_code == 404:
            print(f"Item {item_id} not found.")
            return
        r.raise_for_status()
        print_item(r.json())
    except requests.ConnectionError:
        print("Error: Cannot connect to the API server.")
    except requests.HTTPError as e:
        print(f"Error: {e}")


def add_item():
    print("\nEnter item details (press Enter to leave optional fields blank):")
    product_name = input("  Product name (required): ").strip()
    if not product_name:
        print("Product name is required.")
        return
    brand = input("  Brand: ").strip()
    category = input("  Category: ").strip()
    barcode = input("  Barcode: ").strip()
    unit = input("  Unit (e.g. 500g, 1L): ").strip()
    ingredients = input("  Ingredients: ").strip()
    price = input("  Price (required, e.g. 2.99): ").strip()
    stock = input("  Stock quantity (required): ").strip()

    if not price or not stock:
        print("Price and stock quantity are required.")
        return

    try:
        payload = {
            "product_name": product_name,
            "brand": brand,
            "category": category,
            "barcode": barcode,
            "unit": unit,
            "ingredients_text": ingredients,
            "price": float(price),
            "stock_quantity": int(stock),
        }
    except ValueError:
        print("Invalid price or stock quantity.")
        return

    try:
        r = requests.post(f"{BASE_URL}/inventory", json=payload)
        r.raise_for_status()
        print("\nItem created:")
        print_item(r.json())
    except requests.ConnectionError:
        print("Error: Cannot connect to the API server.")
    except requests.HTTPError as e:
        print(f"Error {r.status_code}: {r.json().get('error')}")


def update_item():
    item_id = input("Enter item ID to update: ").strip()
    if not item_id.isdigit():
        print("Invalid ID.")
        return
    print("What would you like to update?")
    print("  1. Price")
    print("  2. Stock quantity")
    print("  3. Both")
    choice = input("Choice: ").strip()

    payload = {}
    if choice in ("1", "3"):
        price = input("  New price: ").strip()
        try:
            payload["price"] = float(price)
        except ValueError:
            print("Invalid price.")
            return
    if choice in ("2", "3"):
        stock = input("  New stock quantity: ").strip()
        try:
            payload["stock_quantity"] = int(stock)
        except ValueError:
            print("Invalid stock quantity.")
            return
    if not payload:
        print("Nothing to update.")
        return

    try:
        r = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=payload)
        if r.status_code == 404:
            print(f"Item {item_id} not found.")
            return
        r.raise_for_status()
        print("\nItem updated:")
        print_item(r.json())
    except requests.ConnectionError:
        print("Error: Cannot connect to the API server.")
    except requests.HTTPError as e:
        print(f"Error: {e}")


def delete_item():
    item_id = input("Enter item ID to delete: ").strip()
    if not item_id.isdigit():
        print("Invalid ID.")
        return
    confirm = input(f"Delete item {item_id}? (y/N): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return
    try:
        r = requests.delete(f"{BASE_URL}/inventory/{item_id}")
        if r.status_code == 404:
            print(f"Item {item_id} not found.")
            return
        if r.status_code == 204:
            print(f"Item {item_id} deleted.")
            return
        r.raise_for_status()
    except requests.ConnectionError:
        print("Error: Cannot connect to the API server.")
    except requests.HTTPError as e:
        print(f"Error: {e}")


def lookup_product():
    print("\nLook up by:")
    print("  1. Barcode")
    print("  2. Product name")
    choice = input("Choice: ").strip()

    if choice == "1":
        barcode = input("  Barcode: ").strip()
        if not barcode:
            print("Barcode cannot be empty.")
            return
        try:
            r = requests.get(f"{BASE_URL}/inventory/lookup", params={"barcode": barcode})
            if r.status_code == 404:
                print(f"No product found for barcode: {barcode}")
                return
            r.raise_for_status()
            product = r.json()
            print("\nProduct found:")
            print_off_product(product)
            _prompt_add_to_inventory(product)
        except requests.ConnectionError:
            print("Error: Cannot connect to the API server.")
        except requests.HTTPError as e:
            print(f"Error: {e}")

    elif choice == "2":
        name = input("  Product name: ").strip()
        if not name:
            print("Name cannot be empty.")
            return
        try:
            r = requests.get(f"{BASE_URL}/inventory/lookup", params={"name": name})
            r.raise_for_status()
            results = r.json()
            if not results:
                print("No products found.")
                return
            print(f"\nFound {len(results)} result(s):")
            for i, product in enumerate(results, 1):
                print(f"\n[{i}]", end="")
                print_off_product(product)
            sel = input("\nEnter number to add to inventory (or 0 to skip): ").strip()
            if sel.isdigit():
                idx = int(sel)
                if 1 <= idx <= len(results):
                    _prompt_add_to_inventory(results[idx - 1])
        except requests.ConnectionError:
            print("Error: Cannot connect to the API server.")
        except requests.HTTPError as e:
            print(f"Error: {e}")
    else:
        print("Invalid choice.")


def _prompt_add_to_inventory(product):
    confirm = input("\nAdd this item to inventory? (y/N): ").strip().lower()
    if confirm != "y":
        return
    price = input("  Price: ").strip()
    stock = input("  Stock quantity: ").strip()
    try:
        payload = {
            "product_name": product.get("product_name", ""),
            "brand": product.get("brand", ""),
            "category": product.get("category", ""),
            "barcode": product.get("barcode", ""),
            "ingredients_text": product.get("ingredients_text", ""),
            "unit": product.get("quantity", ""),
            "price": float(price),
            "stock_quantity": int(stock),
        }
    except ValueError:
        print("Invalid price or stock quantity.")
        return
    try:
        r = requests.post(f"{BASE_URL}/inventory", json=payload)
        r.raise_for_status()
        print("\nItem added to inventory:")
        print_item(r.json())
    except requests.ConnectionError:
        print("Error: Cannot connect to the API server.")
    except requests.HTTPError:
        print(f"Error {r.status_code}: {r.json().get('error')}")


def print_menu():
    print("\n" + "="*60)
    print("  INVENTORY MANAGEMENT SYSTEM")
    print("="*60)
    print("  1. List all inventory items")
    print("  2. View item by ID")
    print("  3. Add new item")
    print("  4. Update item (price / stock)")
    print("  5. Delete item")
    print("  6. Look up product on OpenFoodFacts")
    print("  7. Exit")
    print("="*60)


def main():
    handlers = {
        "1": list_inventory,
        "2": view_item,
        "3": add_item,
        "4": update_item,
        "5": delete_item,
        "6": lookup_product,
    }
    while True:
        print_menu()
        choice = input("Select an option: ").strip()
        if choice == "7":
            print("Goodbye.")
            sys.exit(0)
        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            print("Invalid option. Please choose 1-7.")


if __name__ == "__main__":
    main()
