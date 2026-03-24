# Inventory Management System

A Flask-based REST API for managing a retail inventory, with OpenFoodFacts integration for real-time product data enrichment and a CLI frontend for interactive use.

## Stack

- Python 3.11
- Flask
- requests
- pytest + unittest.mock

---

## Setup

### Clone and install dependencies

```bash
git clone https://github.com/ronnyabuto/inventory-management-system.git
cd inventory-management-system
pipenv install
pipenv shell
```

---

## Running the API

```bash
python app.py
```

Server starts at `http://localhost:5000`.

---

## API Endpoints

### GET /inventory
Returns all inventory items.

```bash
curl http://localhost:5000/inventory
```

### GET /inventory/\<id\>
Returns a single item by ID.

```bash
curl http://localhost:5000/inventory/1
```

**404** if not found.

### POST /inventory
Creates a new inventory item.

Required fields: `product_name`, `price`, `stock_quantity`

```bash
curl -X POST http://localhost:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Oat Milk", "brand": "Oatly", "price": 2.99, "stock_quantity": 60, "unit": "1L"}'
```

**201** on success, **400** if required fields are missing.

### PATCH /inventory/\<id\>
Updates fields on an existing item (typically `price` and/or `stock_quantity`).

```bash
curl -X PATCH http://localhost:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 5.49, "stock_quantity": 100}'
```

**200** on success, **404** if not found.

### DELETE /inventory/\<id\>
Removes an item.

```bash
curl -X DELETE http://localhost:5000/inventory/3
```

**204** on success, **404** if not found.

### GET /inventory/lookup
Fetches product data from OpenFoodFacts by barcode or name.

```bash
# By barcode
curl "http://localhost:5000/inventory/lookup?barcode=3017620422003"

# By name
curl "http://localhost:5000/inventory/lookup?name=Nutella"
```

**400** if neither parameter is provided. **404** if barcode lookup finds nothing.

---

## Running the CLI

Start the Flask server first, then in a second terminal:

```bash
python cli.py
```

Menu options:
1. List all inventory items
2. View item by ID
3. Add new item
4. Update item (price / stock)
5. Delete item
6. Look up product on OpenFoodFacts (barcode or name)
7. Exit

---

## Running Tests

```bash
pipenv run pytest tests/ -v
```

Test files:
- `tests/test_app.py` — 12 tests covering all API endpoints
- `tests/test_external_api.py` — 6 tests with mocked HTTP calls for OpenFoodFacts integration

---

## Project Structure

```
.
├── app.py              # Flask application and route handlers
├── database.py         # In-memory inventory store with CRUD helpers
├── external_api.py     # OpenFoodFacts API integration
├── cli.py              # Interactive CLI frontend
├── Pipfile
├── Pipfile.lock
├── pytest.ini
├── README.md
└── tests/
    ├── __init__.py
    ├── test_app.py
    └── test_external_api.py
```
