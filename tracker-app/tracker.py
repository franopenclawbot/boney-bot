#!/usr/bin/env python3
"""
Product Stock Tracker CLI
Track out-of-stock products from major retailers
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Configuration
DATA_DIR = Path(__file__).parent / "data"
PRODUCTS_FILE = DATA_DIR / "products.json"
LOGS_DIR = DATA_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


def load_products():
    """Load tracked products from JSON file."""
    if not PRODUCTS_FILE.exists():
        return []
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)


def save_products(products):
    """Save products to JSON file."""
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2)


def add_product(products, name, url):
    """Add a new product to track."""
    product = {
        "name": name,
        "url": url,
        "last_check": None,
        "in_stock": False,
        "out_of_stock_count": 0,
        "last_in_stock": None,
    }
    products.append(product)
    save_products(products)
    print(f"✅ Added: {name}")
    return product


def remove_product(products, index):
    """Remove a product by index."""
    if 0 <= index < len(products):
        removed = products.pop(index)
        save_products(products)
        print(f"❌ Removed: {removed['name']}")
    else:
        print("❌ Invalid index")


def list_products(products):
    """List all tracked products."""
    if not products:
        print("No products being tracked.")
        return

    print("\n📊 Tracked Products:")
    print("-" * 60)
    for i, p in enumerate(products):
        status = "✅ In Stock" if p["in_stock"] else "❌ Out of Stock"
        print(f"{i}: {p['name']}")
        print(f"   Status: {status}")
        print(f"   URL: {p['url']}")
        print(f"   Last check: {p['last_check'] or 'Never'}")
        print("-" * 60)


def scrape_stock(url):
    """
    Scrape a product page to check stock status.
    Returns True if in stock, False if out of stock, None if unknown.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️  Request failed: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    # Common out-of-stock indicators
    out_of_stock_patterns = [
        "out of stock",
        "sold out",
        "unavailable",
        "coming soon",
        "backorder",
    ]

    page_text = soup.get_text().lower()

    for pattern in out_of_stock_patterns:
        if pattern in page_text:
            return False

    # If no obvious out-of-stock text, assume in stock
    return True


def check_stock(products):
    """Check stock status for all tracked products."""
    if not products:
        print("No products to check.")
        return

    print("\n🔍 Checking stock status...")
    print("=" * 60)

    for i, p in enumerate(products):
        print(f"\nChecking: {p['name']}")
        print(f"URL: {p['url']}")

        stock_status = scrape_stock(p["url"])

        if stock_status is None:
            print("⚠️  Could not determine stock status")
        elif stock_status:
            if not p["in_stock"]:
                print("✅ NOW IN STOCK!")
                p["last_in_stock"] = datetime.now().isoformat()
                p["out_of_stock_count"] = 0
            p["in_stock"] = True
        else:
            p["out_of_stock_count"] += 1
            p["in_stock"] = False
            print("❌ Out of stock")

        p["last_check"] = datetime.now().isoformat()
        save_products(products)

        # Be respectful to servers
        time.sleep(2)

    print("\n" + "=" * 60)
    print("✅ Stock check complete!")


def main():
    """Main CLI entry point."""
    products = load_products()

    while True:
        print("\n📦 Product Stock Tracker")
        print("=" * 40)
        print("1. List products")
        print("2. Add product")
        print("3. Remove product")
        print("4. Check stock")
        print("5. Exit")
        print("=" * 40)

        choice = input("Choose an option: ").strip()

        if choice == "1":
            list_products(products)
        elif choice == "2":
            name = input("Product name: ").strip()
            url = input("Product URL: ").strip()
            if name and url:
                add_product(products, name, url)
        elif choice == "3":
            list_products(products)
            index = int(input("Enter product index to remove: "))
            remove_product(products, index)
        elif choice == "4":
            check_stock(products)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main()
