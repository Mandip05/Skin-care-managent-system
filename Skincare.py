import os
from datetime import datetime
import getpass
import random
import time
import re
import uuid

class WeCareSystem:
    def __init__(self):
        # Get base folder for storing data
        self.BASE_FOLDER = input("Enter folder name for storing data (default: 'wecare_data'): ").strip() or "wecare_data"
        
        # Create directory structure
        self.setup_directories()
        
        # Setup file paths
        self.PRODUCTS_FILE = os.path.join(self.BASE_FOLDER, "products.txt")
        self.USERS_FILE = os.path.join(self.BASE_FOLDER, "users.txt")
        self.RECOVERY_CODES_FILE = os.path.join(self.BASE_FOLDER, "recovery_codes.txt")
        
        # Create initial files if they don't exist
        self.create_default_files()
        
        # Motivational messages shown after sales
        self.MESSAGES = [
            "You're doing amazing! 💪",
            "Great job closing that sale! 🎉",
            "Keep going, sales star! 🌟",
            "Another happy customer! 😊",
            "You're rocking it! 🔥"
        ]

    def setup_directories(self):
        """Create all required directories for the system"""
        # Main data directory
        os.makedirs(self.BASE_FOLDER, exist_ok=True)
        
        # Reports directories
        self.REPORTS_FOLDER = os.path.join(self.BASE_FOLDER, "reports")
        os.makedirs(self.REPORTS_FOLDER, exist_ok=True)
        
        # Invoices directory
        self.INVOICE_FOLDER = os.path.join(self.REPORTS_FOLDER, "invoices")
        os.makedirs(self.INVOICE_FOLDER, exist_ok=True)
        
        # Customer directory
        self.CUSTOMER_FOLDER = os.path.join(self.INVOICE_FOLDER, "customers")
        os.makedirs(self.CUSTOMER_FOLDER, exist_ok=True)
        
        # Supplier directory
        self.SUPPLIER_FOLDER = os.path.join(self.INVOICE_FOLDER, "suppliers")
        os.makedirs(self.SUPPLIER_FOLDER, exist_ok=True)
        
        # Sales report directory
        self.SALES_REPORTS_FOLDER = os.path.join(self.REPORTS_FOLDER, "sales")
        os.makedirs(self.SALES_REPORTS_FOLDER, exist_ok=True)
        
        # Stock alerts directory
        self.STOCK_ALERTS_FOLDER = os.path.join(self.REPORTS_FOLDER, "stock_alerts")
        os.makedirs(self.STOCK_ALERTS_FOLDER, exist_ok=True)

    def create_default_files(self):
        """Create default files with initial data if they don't exist"""
        # Create default users file with admin account
        if not os.path.exists(self.USERS_FILE):
            with open(self.USERS_FILE, "w") as file:
                file.write("admin,password123,admin@wecare.com,Administrator,12345\n")
        
        # Create default products
        if not os.path.exists(self.PRODUCTS_FILE):
            with open(self.PRODUCTS_FILE, "w") as file:
                file.write("P001, Vitamin C Serum, Garnier, 200, 1000, France\n")
                file.write("P002, Skin Cleanser, Cetaphil, 100, 280, Switzerland\n")
                file.write("P003, Sunscreen, Aqualogica, 200, 700, India\n")
        
        # Create recovery codes file if it doesn't exist
        if not os.path.exists(self.RECOVERY_CODES_FILE):
            open(self.RECOVERY_CODES_FILE, "w").close()

    def display_header(self, title):
        """Display a formatted header for menus"""
        print("\n" + "=" * 50)
        print(f"{title:^50}")
        print("=" * 50)

    def get_password_input(self, prompt="Password: "):
        """Get password input with option to hide or show characters"""
        visibility = input("Do you want to hide your password as you type? (yes/no): ").strip().lower()
        
        if visibility == 'yes':
            try:
                password = getpass.getpass(prompt)
            except Exception:
                print("Hidden input not supported, falling back to visible input.")
                password = input(prompt + " (visible): ")
        else:
            password = input(prompt + " (visible): ")
        
        return password

    def validate_password(self, password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
            
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
            
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
            
        return True, "Password is strong"

    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True
        return False

    def register_user(self):
        """Register a new user"""
        self.display_header("User Registration")
        
        # Get user details with validation
        username = input("Enter desired username: ").strip()
        
        # Check if username already exists
        users = self.read_users()
        if any(user['username'] == username for user in users):
            print("❌ Username already exists. Please choose another one.")
            return
        
        # Get and validate password
        while True:
            password = self.get_password_input("Create password: ")
            valid, message = self.validate_password(password)
            if valid:
                print("✅ " + message)
                break
            else:
                print("❌ " + message)
        
        # Get and validate email
        while True:
            email = input("Enter your email: ").strip()
            if self.validate_email(email):
                break
            else:
                print("❌ Invalid email format. Please try again.")
        
        full_name = input("Enter your full name: ").strip()
        phone = input("Enter your phone number: ").strip()
        
        # Add new user
        with open(self.USERS_FILE, "a") as file:
            file.write(f"{username},{password},{email},{full_name},{phone}\n")
        
        print("\n✅ Registration successful! You can now login with your new account.")
        time.sleep(1.5)

    def read_users(self):
        """Read all users from the users file"""
        users = []
        with open(self.USERS_FILE, "r") as file:
            for line in file:
                parts = [x.strip() for x in line.strip().split(",")]
                if len(parts) >= 5:
                    users.append({
                        "username": parts[0],
                        "password": parts[1],
                        "email": parts[2],
                        "full_name": parts[3],
                        "phone": parts[4]
                    })
        return users

    def write_users(self, users):
        """Write users list back to the file"""
        with open(self.USERS_FILE, "w") as file:
            for user in users:
                line = f"{user['username']},{user['password']},{user['email']},{user['full_name']},{user['phone']}\n"
                file.write(line)

    def verify_user(self, username, password):
        """Verify user credentials"""
        users = self.read_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                return True
        return False

    def forgot_password(self):
        """Password recovery functionality"""
        self.display_header("Password Recovery")
        
        username = input("Enter your username: ").strip()
        email = input("Enter your registered email: ").strip()
        
        users = self.read_users()
        found = False
        
        for user in users:
            if user['username'] == username and user['email'] == email:
                found = True
                # Generate a recovery code
                recovery_code = str(uuid.uuid4())[:8]
                
                # Save recovery code
                with open(self.RECOVERY_CODES_FILE, "a") as file:
                    file.write(f"{username},{recovery_code},{datetime.now().isoformat()}\n")
                
                print(f"\n✅ Recovery code generated successfully!")
                print(f"Your recovery code is: {recovery_code}")
                print("(In a real system, this would be sent to your email)")
                
                use_now = input("\nDo you want to reset your password now? (yes/no): ").strip().lower()
                if use_now == 'yes':
                    self.reset_password(username, recovery_code)
                break
        
        if not found:
            print("❌ No matching username and email found.")

    def reset_password(self, username=None, provided_code=None):
        """Reset user password using recovery code"""
        self.display_header("Password Reset")
        
        if username is None:
            username = input("Enter your username: ").strip()
        
        if provided_code is None:
            provided_code = input("Enter your recovery code: ").strip()
        
        # Verify recovery code
        valid_code = False
        recovery_codes = []
        with open(self.RECOVERY_CODES_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    recovery_codes.append(parts)
                    if parts[0] == username and parts[1] == provided_code:
                        valid_code = True
        
        if not valid_code:
            print("❌ Invalid recovery code.")
            return
        
        # Set new password
        users = self.read_users()
        for user in users:
            if user['username'] == username:
                while True:
                    new_password = self.get_password_input("Enter new password: ")
                    valid, message = self.validate_password(new_password)
                    if valid:
                        user['password'] = new_password
                        self.write_users(users)
                        
                        # Remove used recovery code
                        updated_codes = [code for code in recovery_codes if not (code[0] == username and code[1] == provided_code)]
                        with open(self.RECOVERY_CODES_FILE, "w") as file:
                            for code in updated_codes:
                                file.write(f"{','.join(code)}\n")
                        
                        print("\n✅ Password reset successfully!")
                        time.sleep(1.5)
                        return
                    else:
                        print("❌ " + message)

    def login(self):
        """Handle user login"""
        self.display_header("WeCare Login")
        
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            username = input("Username: ")
            password = self.get_password_input()
            
            if self.verify_user(username, password):
                print("\n✅ Login successful!")
                time.sleep(1)
                return username
            else:
                attempts += 1
                remaining = max_attempts - attempts
                print(f"❌ Invalid credentials. {remaining} attempts remaining.")
                
                if remaining > 0:
                    forgot = input("Forgot password? (yes/no): ").strip().lower()
                    if forgot == 'yes':
                        self.forgot_password()
        
        print("\n❌ Too many failed attempts. Please try again later.")
        return None

    def read_products(self):
        """Read products from file"""
        products = {}
        with open(self.PRODUCTS_FILE, "r") as file:
            for line in file:
                parts = [x.strip() for x in line.strip().split(",")]
                if len(parts) >= 6:
                    pid, name, brand, qty, cost, origin = parts
                    products[pid] = {
                        "id": pid,
                        "name": name,
                        "brand": brand,
                        "quantity": int(qty),
                        "cost_price": float(cost),
                        "origin": origin
                    }
        return products

    def write_products(self, products):
        """Write products back to file"""
        with open(self.PRODUCTS_FILE, "w") as file:
            for p in products.values():
                line = f"{p['id']}, {p['name']}, {p['brand']}, {p['quantity']}, {p['cost_price']}, {p['origin']}\n"
                file.write(line)

    def display_products(self, products):
        """Display all products"""
        self.display_header("Available Products")
        
        if not products:
            print("No products available.")
            return
            
        print(f"{'ID':<8} {'Product':<20} {'Brand':<15} {'Price (Rs)':<12} {'Qty':<8} {'Origin':<15}")
        print("-" * 80)
        
        for p in products.values():
            selling_price = p['cost_price'] * 2
            print(f"{p['id']:<8} {p['name']:<20} {p['brand']:<15} {selling_price:,.2f}{'Rs':<8} {p['quantity']:<8} {p['origin']:<15}")

    def search_products(self, products):
        """Search products by name, brand or country"""
        keyword = input("Enter product name, brand or country to search: ").lower()
        
        self.display_header(f"Search Results for '{keyword}'")
        
        found = False
        print(f"{'ID':<8} {'Product':<20} {'Brand':<15} {'Price (Rs)':<12} {'Qty':<8} {'Origin':<15}")
        print("-" * 80)
        
        for p in products.values():
            if (keyword in p['name'].lower() or 
                keyword in p['brand'].lower() or 
                keyword in p['origin'].lower()):
                
                selling_price = p['cost_price'] * 2
                print(f"{p['id']:<8} {p['name']:<20} {p['brand']:<15} {selling_price:,.2f}{'Rs':<8} {p['quantity']:<8} {p['origin']:<15}")
                found = True
                
        if not found:
            print("No matching products found.")

    def generate_invoice(self, customer_name, invoice_lines, total, is_customer=True):
        """Generate and save invoice file"""
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = customer_name.replace(' ', '_')
        
        if is_customer:
            folder = self.CUSTOMER_FOLDER
            prefix = "customer"
        else:
            folder = self.SUPPLIER_FOLDER
            prefix = "supplier"
            
        filename = f"invoice_{prefix}_{safe_name}_{date_str}.txt"
        filepath = os.path.join(folder, filename)
        
        content = [
            f"{'WeCare Store':^50}",
            f"{'':=^50}",
            f"{prefix.capitalize()}: {customer_name}",
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n"
        ]
        
        if is_customer:
            content.append("Items Purchased:")
        else:
            content.append("Items Restocked:")
            
        content.extend(invoice_lines)
        content.append("\n")
        content.append(f"Total {'Amount' if is_customer else 'Cost'}: Rs. {total:,.2f}")
        
        with open(filepath, "w") as file:
            file.write("\n".join(content))
            
        return filename

    def update_sales_report(self, sold_items, total, username):
        """Update sales report with new sales data"""
        # Create daily sales report file
        date_str = datetime.now().strftime("%Y-%m-%d")
        report_file = os.path.join(self.SALES_REPORTS_FOLDER, f"sales_report_{date_str}.txt")
        
        # Check if file exists and add header if new
        file_exists = os.path.exists(report_file)
        
        with open(report_file, "a") as file:
            if not file_exists:
                file.write(f"{'WeCare Daily Sales Report':^50}\n")
                file.write(f"{'Date: ' + date_str:^50}\n")
                file.write("=" * 50 + "\n\n")
            
            time_str = datetime.now().strftime("%H:%M:%S")
            file.write(f"Time: {time_str}  |  Staff: {username}\n")
            file.write("-" * 50 + "\n")
            
            for name, brand, qty, cost in sold_items:
                file.write(f"{name} ({brand}) - Qty: {qty}, Rs. {cost:,.2f}\n")
            
            file.write(f"Total Sale: Rs. {total:,.2f}\n")
            file.write("-" * 50 + "\n\n")

    def view_sales_report(self):
        """View and navigate through sales reports"""
        self.display_header("Sales Reports")
        
        # Get list of report files
        report_files = sorted([f for f in os.listdir(self.SALES_REPORTS_FOLDER) 
                             if f.startswith("sales_report_")])
        
        if not report_files:
            print("No sales reports found.")
            input("\nPress Enter to continue...")
            return
            
        # Display available reports
        print("Available Reports:")
        for i, report in enumerate(report_files, 1):
            date = report.replace("sales_report_", "").replace(".txt", "")
            print(f"{i}. Sales Report - {date}")
            
        # Ask user which report to view
        while True:
            try:
                choice = input("\nEnter report number to view (or '0' to return): ")
                if choice == '0':
                    return
                    
                index = int(choice) - 1
                if 0 <= index < len(report_files):
                    # Display selected report
                    with open(os.path.join(self.SALES_REPORTS_FOLDER, report_files[index]), "r") as file:
                        print("\n" + "=" * 50)
                        print(file.read())
                    
                    input("\nPress Enter to continue...")
                    return
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def stock_alert(self, products):
        """Generate and display stock alerts"""
        self.display_header("Stock Alerts")
        
        low_stock = []
        for p in products.values():
            if p['quantity'] < 10:
                low_stock.append(p)
                print(f"⚠️  Low stock alert for {p['name']} ({p['brand']}) - Only {p['quantity']} left!")
        
        if not low_stock:
            print("All products have sufficient stock levels.")
            return
            
        # Generate stock alert report
        date_str = datetime.now().strftime("%Y-%m-%d")
        alert_file = os.path.join(self.STOCK_ALERTS_FOLDER, f"stock_alert_{date_str}.txt")
        
        with open(alert_file, "w") as file:
            file.write(f"{'WeCare Stock Alert Report':^50}\n")
            file.write(f"{'Date: ' + date_str:^50}\n")
            file.write("=" * 50 + "\n\n")
            
            for p in low_stock:
                file.write(f"⚠️  {p['name']} ({p['brand']}) - Current Stock: {p['quantity']}\n")
                file.write(f"    Product ID: {p['id']}\n")
                file.write(f"    Cost Price: Rs. {p['cost_price']:,.2f}\n")
                file.write(f"    Origin: {p['origin']}\n\n")
        
        print(f"\nStock alert report saved as: stock_alert_{date_str}.txt")

    def sell_product(self, products, username):
        """Process product sales"""
        self.display_header("Sell Products")
        
        customer = input("Enter customer name: ")
        total = 0
        sold_items = []
        invoice_lines = []
        
        while True:
            pid = input("\nEnter product ID to sell (or 'done'): ").strip()
            if pid.lower() == 'done':
                break
                
            if pid not in products:
                print("❌ Product not found.")
                continue
                
            try:
                qty = int(input("Enter quantity to buy: "))
                if qty <= 0:
                    print("❌ Quantity must be positive.")
                    continue
            except ValueError:
                print("❌ Invalid quantity. Please enter a number.")
                continue
            
            product = products[pid]
            if qty > product['quantity']:
                print(f"❌ Not enough stock. Only {product['quantity']} available.")
                continue
            
            # Calculate free items (buy 2 get 1 free)
            free_qty = qty // 3
            total_qty = qty + free_qty
            
            # Calculate cost (customer only pays for non-free items)
            selling_price = product['cost_price'] * 2
            cost = qty * selling_price
            
            # Update totals and reduce inventory
            total += cost
            product['quantity'] -= total_qty
            
            # Record sale
            sold_items.append((product['name'], product['brand'], qty, cost))
            
            # Add to invoice
            invoice_lines.append(f"{product['name']} ({product['brand']}):")
            invoice_lines.append(f"  - Quantity: {qty} + {free_qty} free")
            invoice_lines.append(f"  - Price: Rs. {selling_price:,.2f} each")
            invoice_lines.append(f"  - Subtotal: Rs. {cost:,.2f}")
            invoice_lines.append("")
        
        if sold_items:
            # Generate and save invoice
            filename = self.generate_invoice(customer, invoice_lines, total, is_customer=True)
            
            # Update sales report
            self.update_sales_report(sold_items, total, username)
            
            # Display success message
            print(f"\n✅ Sale completed successfully!")
            print(f"Invoice saved as: {filename}")
            print(random.choice(self.MESSAGES))
            
            # Return to update inventory
            return True
        
        return False

    def restock_product(self, products, username):
        """Process product restocking"""
        self.display_header("Restock Products")
        
        supplier = input("Enter supplier name: ")
        total = 0
        added_items = []
        invoice_lines = []
        
        while True:
            print("\nEnter 'done' at any time to finish restocking")
            
            pid = input("Enter product ID to restock: ").strip()
            if pid.lower() == 'done':
                break
            
            # For existing products, pre-fill information
            if pid in products:
                p = products[pid]
                print(f"Product found: {p['name']} ({p['brand']})")
                print(f"Current stock: {p['quantity']}")
                name = input(f"Enter product name [{p['name']}]: ").strip() or p['name']
                brand = input(f"Enter brand [{p['brand']}]: ").strip() or p['brand']
                origin = input(f"Enter country of origin [{p['origin']}]: ").strip() or p['origin']
            else:
                print("Adding new product...")
                name = input("Enter product name: ")
                if name.lower() == 'done':
                    break
                brand = input("Enter brand: ")
                if brand.lower() == 'done':
                    break
                origin = input("Enter country of origin: ")
                if origin.lower() == 'done':
                    break
            
            try:
                qty = input("Enter quantity to add: ")
                if qty.lower() == 'done':
                    break
                qty = int(qty)
                if qty <= 0:
                    print("❌ Quantity must be positive.")
                    continue
                
                cost = input("Enter cost price per unit: ")
                if cost.lower() == 'done':
                    break
                cost = float(cost)
                if cost <= 0:
                    print("❌ Cost must be positive.")
                    continue
            except ValueError:
                print("❌ Invalid input. Please enter numbers only.")
                continue
            
            # Update existing product or add new one
            if pid in products:
                products[pid]['quantity'] += qty
                products[pid]['cost_price'] = cost  # Update cost price
                products[pid]['name'] = name
                products[pid]['brand'] = brand
                products[pid]['origin'] = origin
            else:
                products[pid] = {
                    "id": pid,
                    "name": name,
                    "brand": brand,
                    "quantity": qty,
                    "cost_price": cost,
                    "origin": origin
                }
            
            # Calculate total cost
            subtotal = qty * cost
            total += subtotal
            
            # Record restock
            added_items.append((name, brand, qty, cost))
            
            # Add to invoice
            invoice_lines.append(f"{name} ({brand}):")
            invoice_lines.append(f"  - Quantity: {qty}")
            invoice_lines.append(f"  - Cost: Rs. {cost:,.2f} each")
            invoice_lines.append(f"  - Subtotal: Rs. {subtotal:,.2f}")
            invoice_lines.append("")
            
            print(f"✅ Added {qty} units of {name}")
        
        if added_items:
            # Generate and save invoice
            filename = self.generate_invoice(supplier, invoice_lines, total, is_customer=False)
            
            # Display success message
            print(f"\n✅ Restock completed successfully!")
            print(f"Invoice saved as: {filename}")
            
            # Return to update inventory
            return True
        
        return False

    def display_startup_screen(self):
        """Display welcome screen"""
        print("\n" + "=" * 60)
        print(f"{'WeCare Store Management System':^60}")
        print(f"{'Version 2.0':^60}")
        print("=" * 60)
        print(f"{'Welcome to your complete store management solution':^60}")
        print(f"{'Developed by: Your Name':^60}")
        print("=" * 60)
        time.sleep(1)

    def main_menu(self, username):
        """Main program menu"""
        while True:
            products = self.read_products()
            
            self.display_header(f"WeCare Store Management - Logged in as: {username}")
            
            print("1. Display Products")
            print("2. Search Products")
            print("3. Sell Products")
            print("4. Restock Products")
            print("5. Stock Alerts")
            print("6. View Sales Reports")
            print("7. Change Password")
            print("8. Logout")
            print("9. Exit Program")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.display_products(products)
                input("\nPress Enter to continue...")
            
            elif choice == '2':
                self.search_products(products)
                input("\nPress Enter to continue...")
            
            elif choice == '3':
                if self.sell_product(products, username):
                    self.write_products(products)
                input("\nPress Enter to continue...")
            
            elif choice == '4':
                if self.restock_product(products, username):
                    self.write_products(products)
                input("\nPress Enter to continue...")
            
            elif choice == '5':
                self.stock_alert(products)
                input("\nPress Enter to continue...")
            
            elif choice == '6':
                self.view_sales_report()
            
            elif choice == '7':
                # Change password
                current_password = self.get_password_input("Enter current password: ")
                if self.verify_user(username, current_password):
                    while True:
                        new_password = self.get_password_input("Enter new password: ")
                        valid, message = self.validate_password(new_password)
                        if valid:
                            # Update password
                            users = self.read_users()
                            for user in users:
                                if user['username'] == username:
                                    user['password'] = new_password
                                    break
                            self.write_users(users)
                            print("\n✅ Password changed successfully!")
                            break
                        else:
                            print("❌ " + message)
                else:
                    print("❌ Current password is incorrect.")
                input("\nPress Enter to continue...")
            
            elif choice == '8':
                print("\nLogging out...")
                time.sleep(1)
                return 'logout'
            
            elif choice == '9':
                print("\nExiting program. Thank you for using WeCare Store Management!")
                return 'exit'
            
            else:
                print("\n❌ Invalid choice. Please try again.")
                time.sleep(1)

    def auth_menu(self):
        """Authentication menu"""
        while True:
            self.display_header("WeCare Authentication")
            
            print("1. Login")
            print("2. Register")
            print("3. Forgot Password")
            print("4. Exit")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                username = self.login()
                if username:
                    result = self.main_menu(username)
                    if result == 'exit':
                        return False
            
            elif choice == '2':
                self.register_user()
            
            elif choice == '3':
                self.forgot_password()
            
            elif choice == '4':
                print("\nExiting program. Thank you for using WeCare Store Management!")
                return False
            
            else:
                print("\n❌ Invalid choice. Please try again.")
                time.sleep(1)

    def run(self):
        """Main program entry point"""
        self.display_startup_screen()
        self.auth_menu()

# Run the application
if __name__ == "__main__":
    wecare = WeCareSystem()
    wecare.run()