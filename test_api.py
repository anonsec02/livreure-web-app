#!/usr/bin/env python3
"""
Comprehensive API Test Suite for Livreure Web App.

This script tests various API endpoints including configuration, restaurants,
delivery zones, and subscription plans. It also includes tests for user
authentication (registration and login) for different user types.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_api_endpoint(endpoint, method="GET", data=None, headers=None):
    url = f"{BASE_URL}{endpoint}"
    print(f"\nTesting {method} {url}")
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return None

        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
        except json.JSONDecodeError:
            print(f"Response Text: {response.text}")
        return response
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}. Make sure the Flask server is running.")
        return None

# Test 1: Get Config
test_api_endpoint("/api/config")

# Test 2: Get Restaurants
test_api_endpoint("/api/restaurants")

# Test 3: Get Delivery Zones
test_api_endpoint("/api/delivery/zones")

# Test 4: Get Subscription Plans
test_api_endpoint("/api/subscription/plans")

# Test 5: User Registration (Customer)
print("\n--- Testing Customer Registration ---")
register_data_customer = {
    "email": "test_customer@example.com",
    "password": "password123",
    "user_type": "customer",
    "name": "Test Customer",
    "phone_number": "1234567890"
}
response_register_customer = test_api_endpoint("/auth/register", method="POST", data=register_data_customer)

# Test 6: User Login (Customer)
print("\n--- Testing Customer Login ---")
login_data_customer = {
    "email": "test_customer@example.com",
    "password": "password123",
    "user_type": "customer"
}
response_login_customer = test_api_endpoint("/auth/login", method="POST", data=login_data_customer)

customer_token = None
if response_login_customer and response_login_customer.status_code == 200:
    customer_token = response_login_customer.json().get("access_token")
    print(f"Customer Token: {customer_token}")

# Test 7: User Registration (Restaurant)
print("\n--- Testing Restaurant Registration ---")
register_data_restaurant = {
    "email": "test_restaurant@example.com",
    "password": "password123",
    "user_type": "restaurant",
    "name": "Test Restaurant",
    "address": "123 Food St",
    "phone_number": "0987654321"
}
response_register_restaurant = test_api_endpoint("/auth/register", method="POST", data=register_data_restaurant)

# Test 8: User Login (Restaurant)
print("\n--- Testing Restaurant Login ---")
login_data_restaurant = {
    "email": "test_restaurant@example.com",
    "password": "password123",
    "user_type": "restaurant"
}
response_login_restaurant = test_api_endpoint("/auth/login", method="POST", data=login_data_restaurant)

restaurant_token = None
if response_login_restaurant and response_login_restaurant.status_code == 200:
    restaurant_token = response_login_restaurant.json().get("access_token")
    print(f"Restaurant Token: {restaurant_token}")

# Test 9: User Registration (Delivery Agent)
print("\n--- Testing Delivery Agent Registration ---")
register_data_delivery = {
    "email": "test_delivery@example.com",
    "password": "password123",
    "user_type": "delivery_agent",
    "name": "Test Delivery",
    "phone_number": "1122334455",
    "vehicle_type": "Motorcycle"
}
response_register_delivery = test_api_endpoint("/auth/register", method="POST", data=register_data_delivery)

# Test 10: User Login (Delivery Agent)
print("\n--- Testing Delivery Agent Login ---")
login_data_delivery = {
    "email": "test_delivery@example.com",
    "password": "password123",
    "user_type": "delivery_agent"
}
response_login_delivery = test_api_endpoint("/auth/login", method="POST", data=login_data_delivery)

delivery_token = None
if response_login_delivery and response_login_delivery.status_code == 200:
    delivery_token = response_login_delivery.json().get("access_token")
    print(f"Delivery Agent Token: {delivery_token}")

# Test 11: Accessing a protected endpoint (example: customer profile)
if customer_token:
    print("\n--- Testing Protected Customer Endpoint ---")
    headers = {"Authorization": f"Bearer {customer_token}"}
    test_api_endpoint("/api/customer/profile", headers=headers)
else:
    print("\nSkipping protected customer endpoint test: No customer token available.")

# Test 12: Accessing a protected endpoint (example: restaurant menu)
if restaurant_token:
    print("\n--- Testing Protected Restaurant Endpoint ---")
    headers = {"Authorization": f"Bearer {restaurant_token}"}
    test_api_endpoint("/api/restaurant/menu", headers=headers)
else:
    print("\nSkipping protected restaurant endpoint test: No restaurant token available.")

# Test 13: Accessing a protected endpoint (example: delivery agent status)
if delivery_token:
    print("\n--- Testing Protected Delivery Agent Endpoint ---")
    headers = {"Authorization": f"Bearer {delivery_token}"}
    test_api_endpoint("/api/delivery/status", headers=headers)
else:
    print("\nSkipping protected delivery agent endpoint test: No delivery agent token available.")

# Test 14: Testing enhanced API endpoint (example: search restaurants by name)
print("\n--- Testing Enhanced API: Search Restaurants by Name ---")
search_data = {"query": "Test Restaurant"}
test_api_endpoint("/api/search/restaurants", method="POST", data=search_data)

# Test 15: Testing subscription API endpoint (example: get user subscription status)
if customer_token:
    print("\n--- Testing Subscription API: Get User Subscription Status ---")
    headers = {"Authorization": f"Bearer {customer_token}"}
    test_api_endpoint("/api/subscription/status", headers=headers)
else:
    print("\nSkipping subscription API test: No customer token available.")


