import sqlite3
import uuid
import re
import random
from datetime import datetime
import os
from tkinter import messagebox, ttk, scrolledtext
import tkinter as tk
from pathlib import Path  # Added for stock_alert
import logging
from .database import DatabaseManager
from .notifications import NotificationService
from .ecommerce import ECommerceIntegration
from .gui import WeCareGUI

class WeCareSystem:
    def __init__(self, root):  # Add root parameter
        self.root = root  # Store root
        self.db = DatabaseManager()
        self.notification = NotificationService()
        self.ecommerce = ECommerceIntegration()
        self.MESSAGES = [
            "You're doing amazing! 💪",
            "Great job closing that sale! 🎉",
            "Keep going, sales star! 🌟",
            "Another happy customer! 😊",
            "You're rocking it! 🔥"
        ]
        self.current_user = None
        self.gui = WeCareGUI(self.root, self)

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
        return bool(re.match(pattern, email))

    def login(self):
        """Handle user login"""
        username = self.gui.login_username.get().strip()
        password = self.gui.login_password.get().strip()
        
        try:
            with sqlite3.connect(self.db.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT password, email FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                
                if result and result[0] == password:
                    self.current_user = username
                    self.gui.notebook.select(self.gui.main_frame)
                    messagebox.showinfo("Success", "Login successful!")
                    self.notification.send_email(result[1], "Login Notification", 
                                               f"User {username} logged in at {datetime.now()}")
                else:
                    messagebox.showerror("Error", "Invalid credentials")
        except sqlite3.Error as e:
            logging.error(f"Login error: {e}")
            messagebox.showerror("Error", "Database error occurred")

    def register_user(self):
        """Register a new user"""
        data = {k: v.get() for k, v in self.gui.register_entries.items()}
        
        try:
            if not all(data.values()):
                messagebox.showerror("Error", "All fields are required")
                return

            if not self.validate_email(data['email']):
                messagebox.showerror("Error", "Invalid email format")
                return

            valid, message = self.validate_password(data['password'])
            if not valid:
                messagebox.showerror("Error", message)
                return

            with sqlite3.connect(self.db.db_name) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                                 (data['username'], data['password'], data['email'], 
                                  data['full_name'], data['phone']))
                    conn.commit()
                    messagebox.showinfo("Success", "Registration successful!")
                    self.notification.send_email(data['email'], "Welcome to WeCare",
                                               f"Welcome {data['full_name']} to WeCare Store!")
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Username or email already exists")
        except sqlite3.Error as e:
            logging.error(f"Registration error: {e}")
            messagebox.showerror("Error", "Database error occurred")

    def forgot_password(self):
        """Password recovery functionality"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Password Recovery")
        dialog.geometry("300x200")

        ttk.Label(dialog, text="Username:").pack()
        username_entry = ttk.Entry(dialog)
        username_entry.pack()

        ttk.Label(dialog, text="Email:").pack()
        email_entry = ttk.Entry(dialog)
        email_entry.pack()

        def submit():
            username = username_entry.get()
            email = email_entry.get()

            try:
                with sqlite3.connect(self.db.db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT email FROM users WHERE username = ?", (username,))
                    result = cursor.fetchone()

                    if result and result[0] == email:
                        recovery_code = str(uuid.uuid4())[:8]
                        cursor.execute("INSERT INTO recovery_codes VALUES (?, ?, ?)",
                                     (username, recovery_code, datetime.now().isoformat()))
                        conn.commit()
                        
                        self.notification.send_email(email, "Password Recovery Code",
                                                   f"Your recovery code is: {recovery_code}")
                        messagebox.showinfo("Success", f"Recovery code sent to {email}")
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Invalid username or email")
            except sqlite3.Error as e:
                logging.error(f"Password recovery error: {e}")
                messagebox.showerror("Error", "Database error occurred")

        ttk.Button(dialog, text="Submit", command=submit).pack(pady=10)

    def change_password(self):
        """Change user password"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Password")
        dialog.geometry("300x200")

        ttk.Label(dialog, text="Current Password:").pack()
        current_pass = ttk.Entry(dialog, show="*")
        current_pass.pack()

        ttk.Label(dialog, text="New Password:").pack()
        new_pass = ttk.Entry(dialog, show="*")
        new_pass.pack()

        def submit():
            try:
                with sqlite3.connect(self.db.db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT password FROM users WHERE username = ?",
                                  (self.current_user,))
                    if cursor.fetchone()[0] == current_pass.get():
                        valid, message = self.validate_password(new_pass.get())
                        if valid:
                            cursor.execute("UPDATE users SET password = ? WHERE username = ?",
                                          (new_pass.get(), self.current_user))
                            conn.commit()
                            messagebox.showinfo("Success", "Password changed successfully!")
                            dialog.destroy()
                        else:
                            messagebox.showerror("Error", message)
                    else:
                        messagebox.showerror("Error", "Current password incorrect")
            except sqlite3.Error as e:
                logging.error(f"Password change error: {e}")
                messagebox.showerror("Error", "Database error occurred")

        ttk.Button(dialog, text="Submit", command=submit).pack(pady=10)

    def display_products(self):
        """Display all products in treeview"""
        for item in self.gui.products_tree.get_children():
            self.gui.products_tree.delete(item)

        try:
            with sqlite3.connect(self.db.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM products")
                for row in cursor.fetchall():
                    selling_price = row[6] * 2
                    self.gui.products_tree.insert("", "end", values=(
                        row[0], row[1], row[2], row[3], row[4], f"Rs. {selling_price:,.2f}", row[5], row[7]))
                    
                    self.ecommerce.sync_product({
                        'id': row[0], 'name': row[1], 'brand': row[2], 
                        'category': row[3], 'subcategory': row[4], 
                        'price': selling_price, 'quantity': row[5]
                    })
        except sqlite3.Error as e:
            logging.error(f"Product display error: {e}")
            messagebox.showerror("Error", "Failed to load products")

    def search_products(self):
        """Search products by name, brand, category, or country"""
        keyword = self.gui.product_search.get().lower()
        
        for item in self.gui.products_tree.get_children():
            self.gui.products_tree.delete(item)

        try:
            with sqlite3.connect(self.db.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM products 
                    WHERE LOWER(name) LIKE ? OR LOWER(brand) LIKE ? 
                    OR LOWER(category) LIKE ? OR LOWER(origin) LIKE ?
                """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
                
                for row in cursor.fetchall():
                    selling_price = row[6] * 2
                    self.gui.products_tree.insert("", "end", values=(
                        row[0], row[1], row[2], row[3], row[4], f"Rs. {selling_price:,.2f}", row[5], row[7]))
        except sqlite3.Error as e:
            logging.error(f"Product search error: {e}")
            messagebox.showerror("Error", "Failed to search products")

    def add_customer(self):
        """Add new customer"""
        data = {k: v.get() for k, v in self.gui.customer_entries.items()}
        
        try:
            if not data['name']:
                messagebox.showerror("Error", "Customer name is required")
                return

            customer_id = str(uuid.uuid4())
            with sqlite3.connect(self.db.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO customers VALUES (?, ?, ?, ?, ?)",
                              (customer_id, data['name'], data['email'], 
                               data['phone'], data['address']))
                conn.commit()
                messagebox.showinfo("Success", "Customer added successfully!")
                self.notification.send_sms(data['phone'], f"Welcome {data['name']} to WeCare Store!")
        except sqlite3.Error as e:
            logging.error(f"Customer add error: {e}")
            messagebox.showerror("Error", "Failed to add customer")

    def sell_product(self):
        """Process product sales"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Sell Products")
        dialog.geometry("400x500")

        ttk.Label(dialog, text="Customer Name:").pack()
        customer_name = ttk.Entry(dialog)
        customer_name.pack()

        ttk.Label(dialog, text="Product ID:").pack()
        product_id = ttk.Entry(dialog)
        product_id.pack()

        ttk.Label(dialog, text="Quantity:").pack()
        quantity = ttk.Entry(dialog)
        quantity.pack()

        payment_methods = ["Cash", "Credit Card", "UPI"]
        ttk.Label(dialog, text="Payment Method:").pack()
        payment_method = ttk.Combobox(dialog, values=payment_methods)
        payment_method.pack()

        def submit():
            try:
                with sqlite3.connect(self.db.db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id.get(),))
                    product = cursor.fetchone()
                    
                    if not product:
                        messagebox.showerror("Error", "Product not found")
                        return

                    qty = int(quantity.get())
                    if qty <= 0:
                        messagebox.showerror("Error", "Quantity must be positive")
                        return

                    if qty > product[5]:
                        messagebox.showerror("Error", f"Only {product[5]} available")
                        return

                    free_qty = qty // 3
                    total_qty = qty + free_qty
                    selling_price = product[6] * 2
                    total = qty * selling_price

                    cursor.execute("UPDATE products SET quantity = quantity - ? WHERE product_id = ?",
                                  (total_qty, product_id.get()))

                    cursor.execute("SELECT customer_id FROM customers WHERE name = ?", (customer_name.get(),))
                    customer = cursor.fetchone()
                    if not customer:
                        customer_id = str(uuid.uuid4())
                        cursor.execute("INSERT INTO customers (customer_id, name) VALUES (?, ?)",
                                      (customer_id, customer_name.get()))
                    else:
                        customer_id = customer[0]

                    purchase_id = str(uuid.uuid4())
                    cursor.execute("INSERT INTO purchases VALUES (?, ?, ?, ?, ?, ?, ?)",
                                  (purchase_id, customer_id, product_id.get(), qty, total, 
                                   payment_method.get(), datetime.now().isoformat()))

                    conn.commit()

                    receipt = f"""
WeCare Store Receipt
==================
Customer: {customer_name.get()}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
------------------
Item: {product[1]} ({product[2]})
Quantity: {qty} + {free_qty} free
Price: Rs. {selling_price:,.2f} each
Payment Method: {payment_method.get()}
------------------
Total: Rs. {total:,.2f}
==================
"""
                    with open(f"receipts/receipt_{purchase_id}.txt", "w") as f:
                        f.write(receipt)

                    messagebox.showinfo("Success", f"Sale completed! {random.choice(self.MESSAGES)}")
                    self.notification.send_email(f"{customer_name.get()}@example.com",
                                               "Purchase Receipt", receipt)
                    dialog.destroy()
            except (sqlite3.Error, ValueError) as e:
                logging.error(f"Sale error: {e}")
                messagebox.showerror("Error", "Failed to process sale")

        ttk.Button(dialog, text="Submit Sale", command=submit).pack(pady=10)

    def restock_product(self):
        """Process product restocking"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Restock Products")
        dialog.geometry("400x500")

        fields = ["Product ID", "Name", "Brand", "Category", "Subcategory", "Quantity", "Cost Price", "Origin"]
        entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(dialog, text=f"{field}:").pack()
            entry = ttk.Entry(dialog)
            entry.pack()
            entries[field.lower().replace(" ", "_")] = entry

        def submit():
            try:
                with sqlite3.connect(self.db.db_name) as conn:
                    cursor = conn.cursor()
                    product_id = entries['product_id'].get()
                    qty = int(entries['quantity'].get())
                    cost = float(entries['cost_price'].get())

                    if qty <= 0 or cost <= 0:
                        messagebox.showerror("Error", "Quantity and cost must be positive")
                        return

                    cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
                    if cursor.fetchone():
                        cursor.execute("""
                            UPDATE products SET quantity = quantity + ?, cost_price = ?,
                            name = ?, brand = ?, category = ?, subcategory = ?, origin = ?
                            WHERE product_id = ?
                        """, (qty, cost, entries['name'].get(), entries['brand'].get(),
                              entries['category'].get(), entries['subcategory'].get(),
                              entries['origin'].get(), product_id))
                    else:
                        cursor.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                      (product_id, entries['name'].get(), entries['brand'].get(),
                                       entries['category'].get(), entries['subcategory'].get(),
                                       qty, cost, entries['origin'].get()))

                    conn.commit()
                    messagebox.showinfo("Success", "Product restocked successfully!")
                    self.ecommerce.sync_product({
                        'id': product_id,
                        'name': entries['name'].get(),
                        'brand': entries['brand'].get(),
                        'category': entries['category'].get(),
                        'subcategory': entries['subcategory'].get(),
                        'quantity': qty,
                        'price': cost * 2
                    })
                    dialog.destroy()
            except (sqlite3.Error, ValueError) as e:
                logging.error(f"Restock error: {e}")
                messagebox.showerror("Error", "Failed to restock product")

        ttk.Button(dialog, text="Submit Restock", command=submit).pack(pady=10)

    def stock_alert(self):
        """Generate and display stock alerts"""
        try:
            with sqlite3.connect(self.db.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM products WHERE quantity < 10")
                low_stock = cursor.fetchall()

                alert_text = "Stock Alerts\n" + "="*50 + "\n"
                for product in low_stock:
                    alert_text += f"⚠️ {product[1]} ({product[2]}) - Only {product[5]} left!\n"

                if not low_stock:
                    alert_text += "All products have sufficient stock levels.\n"

                Path("stock_alerts").mkdir(exist_ok=True)
                with open(f"stock_alerts/alert_{datetime.now().strftime('%Y%m%d')}.txt", "w") as f:
                    f.write(alert_text)

                messagebox.showinfo("Stock Alerts", alert_text)
        except sqlite3.Error as e:
            logging.error(f"Stock alert error: {e}")
            messagebox.showerror("Error", "Failed to generate stock alerts")

    def view_sales_report(self):
        """View sales reports"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Sales Reports")
        dialog.geometry("600x400")

        text_area = scrolledtext.ScrolledText(dialog, height=20)
        text_area.pack(expand=True, fill='both')

        try:
            with sqlite3.connect(self.db.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.purchase_date, c.name, pr.name, p.quantity, p.total, p.payment_method
                    FROM purchases p
                    JOIN customers c ON p.customer_id = c.customer_id
                    JOIN products pr ON p.product_id = pr.product_id
                """)
                
                report = "Sales Report\n" + "="*50 + "\n"
                for row in cursor.fetchall():
                    report += f"Date: {row[0]}\nCustomer: {row[1]}\nProduct: {row[2]}\n"
                    report += f"Quantity: {row[3]}\nTotal: Rs. {row[4]:,.2f}\n"
                    report += f"Payment: {row[5]}\n" + "-"*50 + "\n"

                text_area.insert(tk.END, report)
                text_area.config(state='disabled')
        except sqlite3.Error as e:
            logging.error(f"Sales report error: {e}")
            messagebox.showerror("Error", "Failed to generate sales report")

    def logout(self):
        """Handle logout"""
        self.current_user = None
        self.gui.notebook.select(self.gui.login_frame)
        messagebox.showinfo("Success", "Logged out successfully")

    def run(self):
        """Run the application"""
        try:
            self.db.backup_database()
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Application error: {e}")
            messagebox.showerror("Error", "Application crashed")