import requests
import time

BASE = "https://snackify-backend.onrender.com"

username = f"smoketest_user_{int(time.time())}"
password = "TestPass123!"

print('Registering user:', username)
resp = requests.post(f"{BASE}/api/auth/register", json={"username":"%s" % username,"password":password})
print('Register status:', resp.status_code)
print(resp.text)

print('\nLogging in')
resp = requests.post(f"{BASE}/api/auth/login", json={"username":username,"password":password})
print('Login status:', resp.status_code)
print(resp.text)
if resp.status_code != 200:
    print('Login failed; aborting smoke tests')
    raise SystemExit(1)

token = resp.json().get('token')
headers = {'Authorization': f'Bearer {token}'}

print('\nPlacing order')
order_payload = {
    "restaurant_id": 1,
    "items": [{"name": "Smoke Item", "quantity": 1}],
    "delivery_address": "123 Smoke St",
    "total_price": 9.99
}
resp = requests.post(f"{BASE}/api/orders/place", json=order_payload, headers=headers)
print('Place order status:', resp.status_code)
print(resp.text)

if resp.status_code == 201:
    order_id = resp.json().get('order_id')
    print('\nChecking order status for id', order_id)
    resp2 = requests.get(f"{BASE}/api/orders/{order_id}", headers=headers)
    print('Order status:', resp2.status_code)
    print(resp2.text)
else:
    print('Order placement failed; details above')
