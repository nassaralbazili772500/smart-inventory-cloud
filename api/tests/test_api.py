import json
import urllib.error
import urllib.request


BASE_URL = "http://localhost:8081"


def request(method, path, data=None):
    url = f"{BASE_URL}{path}"

    body = None
    headers = {
        "Accept": "application/json"
    }

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method=method
    )

    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode("utf-8")

            if response_body:
                return response.status, json.loads(response_body)

            return response.status, None

    except urllib.error.HTTPError as error:
        response_body = error.read().decode("utf-8")

        if response_body:
            return error.code, json.loads(response_body)

        return error.code, None


print("=" * 60)
print("SMART INVENTORY CLOUD API - INTEGRATION TEST")
print("=" * 60)


# --------------------------------------------------
# 1. Health Check
# --------------------------------------------------

status, body = request("GET", "/health")

assert status == 200
assert body["status"] == "healthy"
assert body["database"] == "connected"

print("[PASS] Health Check")


# --------------------------------------------------
# 2. Create Product
# --------------------------------------------------

product_data = {
    "name": "Automated Test Product",
    "category": "Testing",
    "quantity": 10,
    "price": 49.99,
    "minimum_stock": 5
}

status, product = request(
    "POST",
    "/api/products",
    product_data
)

assert status == 201

product_id = product["id"]

print(f"[PASS] Create Product - ID {product_id}")


# --------------------------------------------------
# 3. Get Product
# --------------------------------------------------

status, product = request(
    "GET",
    f"/api/products/{product_id}"
)

assert status == 200
assert product["name"] == "Automated Test Product"

print("[PASS] Get Product")


# --------------------------------------------------
# 4. Update Product
# --------------------------------------------------

updated_data = {
    "name": "Updated Automated Product",
    "category": "Testing",
    "quantity": 4,
    "price": 59.99,
    "minimum_stock": 5
}

status, product = request(
    "PUT",
    f"/api/products/{product_id}",
    updated_data
)

assert status == 200
assert product["quantity"] == 4

print("[PASS] Update Product")


# --------------------------------------------------
# 5. Low Stock
# --------------------------------------------------

status, products = request(
    "GET",
    "/api/products/alerts/low-stock"
)

assert status == 200

ids = [item["id"] for item in products]

assert product_id in ids

print("[PASS] Low Stock Alert")


# --------------------------------------------------
# 6. Search
# --------------------------------------------------

status, products = request(
    "GET",
    "/api/products/filter/search?name=Automated"
)

assert status == 200
assert len(products) >= 1

print("[PASS] Product Search")


# --------------------------------------------------
# 7. Delete Product
# --------------------------------------------------

status, body = request(
    "DELETE",
    f"/api/products/{product_id}"
)

assert status == 204

print("[PASS] Delete Product")


# --------------------------------------------------
# 8. Verify 404
# --------------------------------------------------

status, body = request(
    "GET",
    f"/api/products/{product_id}"
)

assert status == 404
assert body["detail"] == "Product not found"

print("[PASS] Missing Product Returns 404")


# --------------------------------------------------
# Final Result
# --------------------------------------------------

print("=" * 60)
print("ALL INTEGRATION TESTS PASSED")
print("=" * 60)