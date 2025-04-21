import os
from datetime import datetime
import getpass
import random

# Set folder and file paths
INVOICE_FOLDER = "wecare_invoices"
PRODUCTS_FILE = "products.txt"
SALES_REPORT = "sales_report.txt"
os.makedirs(INVOICE_FOLDER, exist_ok=True)

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Motivational messages
MESSAGES = [
    "You're doing amazing! 💪",
    "Great job closing that sale! 🎉",
    "Keep going, sales star! 🌟",
    "Another happy customer! 😊",
    "You're rocking it! 🔥"
]

# Initialize default product file if not exists
def create_default_products_file():
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "w") as file:
            file.write("P001, Vitamin C Serum, Garnier, 200, 1000, France\n")
            file.write("P002, Skin Cleanser, Cetaphil, 100, 280, Switzerland\n")
            file.write("P003, Sunscreen, Aqualogica, 200, 700, India\n")

def read_products():
    products = {}
    with open(PRODUCTS_FILE, "r") as file:
        for line in file:
            pid, name, brand, qty, cost, origin = [x.strip() for x in line.strip().split(",")]
            products[pid] = {
                "id": pid,
                "name": name,
                "brand": brand,
                "quantity": int(qty),
                "cost_price": float(cost),
                "origin": origin
            }
    return products

def write_products(products):
    with open(PRODUCTS_FILE, "w") as file:
        for p in products.values():
            line = f"{p['id']}, {p['name']}, {p['brand']}, {p['quantity']}, {p['cost_price']}, {p['origin']}\n"
            file.write(line)

def display_products(products):
    print("\nAvailable Products:")
    print("-"*80)
    for p in products.values():
        selling_price = p['cost_price'] * 2
        print(f"{p['id']} - {p['name']} ({p['brand']}) - Rs. {selling_price:.2f} - Qty: {p['quantity']} - {p['origin']}")
    print("-"*80)

def search_products(products):
    keyword = input("Enter product name, brand or country to search: ").lower()
    print("\nSearch Results:")
    found = False
    for p in products.values():
        if keyword in p['name'].lower() or keyword in p['brand'].lower() or keyword in p['origin'].lower():
            selling_price = p['cost_price'] * 2
            print(f"{p['id']} - {p['name']} ({p['brand']}) - Rs. {selling_price:.2f} - Qty: {p['quantity']} - {p['origin']}")
            found = True
    if not found:
        print("No matching products found.")

def generate_invoice(filename, content):
    path = os.path.join(INVOICE_FOLDER, filename)
    with open(path, "w") as file:
        file.write(content)

def update_sales_report(sold_items, total):
    with open(SALES_REPORT, "a") as file:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Date: {date}\n")
        for name, brand, qty, cost in sold_items:
            file.write(f"{name} ({brand}) - Qty: {qty}, Rs. {cost:.2f}\n")
        file.write(f"Total Sale: Rs. {total:.2f}\n\n")

def stock_alert(products):
    for p in products.values():
        if p['quantity'] < 10:
            print(f"⚠️  Low stock alert for {p['name']} ({p['brand']}) - Only {p['quantity']} left!")

def sell_product(products):
    customer = input("Enter customer name: ")
    total = 0
    sold_items = []
    invoice_lines = []

    while True:
        pid = input("Enter product ID to sell (or 'done'): ").strip()
        if pid.lower() == 'done':
            break
        if pid not in products:
            print("Product not found.")
            continue
        try:
            qty = int(input("Enter quantity to buy: "))
        except ValueError:
            print("Invalid quantity.")
            continue

        product = products[pid]
        if qty > product['quantity']:
            print("Not enough stock.")
            continue

        free_qty = qty // 3
        total_qty = qty + free_qty
        cost = qty * (product['cost_price'] * 2)
        total += cost
        product['quantity'] -= total_qty
        sold_items.append((product['name'], product['brand'], qty, cost))
        invoice_lines.append(f"{product['name']} ({product['brand']}) - Bought: {qty}, Free: {free_qty}, Rs. {cost:.2f}")

    if sold_items:
        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"invoice_customer_{customer.replace(' ', '_')}_{date}.txt"
        content = f"Customer: {customer}\nDate: {date}\n\nItems Purchased:\n" + "\n".join(invoice_lines)
        content += f"\n\nTotal Amount: Rs. {total:.2f}\n"
        generate_invoice(filename, content)
        update_sales_report(sold_items, total)
        print(random.choice(MESSAGES))
        print(f"Invoice saved as {filename}")

def restock_product(products):
    supplier = input("Enter supplier name: ")
    total = 0
    added_items = []

    while True:
        pid = input("Enter product ID to restock (or 'done'): ").strip()
        if pid.lower() == 'done':
            break
        name = input("Enter product name: ")
        brand = input("Enter brand: ")
        try:
            qty = int(input("Enter quantity: "))
            cost = float(input("Enter new cost price: "))
        except ValueError:
            print("Invalid input.")
            continue
        origin = input("Enter country of origin: ")

        if pid in products:
            products[pid]['quantity'] += qty
            products[pid]['cost_price'] = cost
        else:
            products[pid] = {
                "id": pid,
                "name": name,
                "brand": brand,
                "quantity": qty,
                "cost_price": cost,
                "origin": origin
            }
        total += qty * cost
        added_items.append((name, brand, qty, cost))

    if added_items:
        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"invoice_supplier_{supplier.replace(' ', '_')}_{date}.txt"
        content = f"Supplier: {supplier}\nDate: {date}\n\nItems Restocked:\n"
        for name, brand, qty, cost in added_items:
            content += f"{name} ({brand}) - Quantity: {qty}, Cost: Rs. {cost:.2f}\n"
        content += f"\nTotal Cost: Rs. {total:.2f}\n"
        generate_invoice(filename, content)
        print(f"Restock invoice saved as {filename}")

def admin_login():
    print("\nAdmin Login Required")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def main():
    create_default_products_file()
    if not admin_login():
        print("Access Denied.")
        return

    while True:
        products = read_products()
        print("\n=== WeCare Store Management ===")
        print("1. Display Products")
        print("2. Search Product")
        print("3. Sell Product")
        print("4. Restock Product")
        print("5. Stock Alerts")
        print("6. Exit")
        choice = input("Enter choice: ")
        if choice == '1':
            display_products(products)
        elif choice == '2':
            search_products(products)
        elif choice == '3':
            sell_product(products)
            write_products(products)
        elif choice == '4':
            restock_product(products)
            write_products(products)
        elif choice == '5':
            stock_alert(products)
        elif choice == '6':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()