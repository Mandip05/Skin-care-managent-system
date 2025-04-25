import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import logging

class WeCareGUI:
    def __init__(self, root, system):
        self.root = root
        self.system = system
        self.root.title("WeCare Store Management System")
        self.root.geometry("800x600")
        self.setup_gui()

    def setup_gui(self):
        logging.info("Starting GUI setup")
        self.root.configure(bg="#f0f0f0")
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True, fill='both')

        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Login")
        self.setup_login_frame()

        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Main Menu")
        ttk.Label(self.main_frame, text="Welcome to WeCare!").pack()

        try:
            image = Image.open("D:/skincare/logo.png")
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            label = ttk.Label(self.login_frame, image=photo)
            label.image = photo
            label.pack()
        except Exception as e:
            logging.error(f"Image loading failed: {e}")

        logging.info("GUI setup complete")

    def setup_login_frame(self):
        ttk.Label(self.login_frame, text="Username:").pack()
        self.login_username = ttk.Entry(self.login_frame)
        self.login_username.pack()
        ttk.Label(self.login_frame, text="Password:").pack()
        self.login_password = ttk.Entry(self.login_frame, show="*")
        self.login_password.pack()
        ttk.Button(self.login_frame, text="Login", command=self.system.login).pack(pady=10)

    # Add other frame setups (e.g., setup_customers_frame with grid) as needed

    def setup_register_frame(self):
        """Setup registration GUI"""
        frame = ttk.Frame(self.register_frame, padding="20")
        frame.pack(expand=True, fill='both')

        fields = ["Username", "Password", "Email", "Full Name", "Phone"]
        self.register_entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(frame, show="*" if field == "Password" else "")
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.register_entries[field.lower().replace(" ", "_")] = entry

        ttk.Button(frame, text="Register", command=self.system.register_user).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def setup_main_frame(self):
        """Setup main menu GUI"""
        frame = ttk.Frame(self.main_frame, padding="20")
        frame.pack(expand=True, fill='both')

        buttons = [
            ("View Products", lambda: self.notebook.select(self.products_frame)),
            ("Manage Customers", lambda: self.notebook.select(self.customers_frame)),
            ("Sell Products", self.system.sell_product),
            ("Restock Products", self.system.restock_product),
            ("View Stock Alerts", self.system.stock_alert),
            ("View Sales Reports", self.system.view_sales_report),
            ("Change Password", self.system.change_password),
            ("Logout", self.system.logout)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(frame, text=text, command=command).grid(row=i, column=0, pady=5, sticky='ew')

    def setup_products_frame(self):
        """Setup products management GUI"""
        frame = ttk.Frame(self.products_frame, padding="20")
        frame.pack(expand=True, fill='both')

        # Search
        ttk.Label(frame, text="Search:").pack()
        self.product_search = ttk.Entry(frame)
        self.product_search.pack(fill='x')
        ttk.Button(frame, text="Search", command=self.system.search_products).pack()

        # Products treeview
        self.products_tree = ttk.Treeview(frame, columns=("ID", "Name", "Brand", "Category", "Subcategory", "Price", "Qty", "Origin"), show="headings")
        for col in self.products_tree["columns"]:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)
        self.products_tree.pack(expand=True, fill='both')

        ttk.Button(frame, text="Refresh Products", command=self.system.display_products).pack(pady=5)

    def setup_customers_frame(self):
        """Setup customers management GUI"""
        frame = ttk.Frame(self.customers_frame, padding="20")
        frame.grid(row=0, column=0, sticky="nsew")

        # Customer info
        fields = ["Name", "Email", "Phone", "Address"]
        self.customer_entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(frame)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.customer_entries[field.lower()] = entry

        ttk.Button(frame, text="Add Customer", command=self.system.add_customer).grid(row=len(fields), column=0, columnspan=2, pady=5, sticky="ew")

        # Purchase history
        self.purchase_tree = ttk.Treeview(frame, columns=("ID", "Product", "Qty", "Total", "Date", "Payment"), show="headings")
        for col in self.purchase_tree["columns"]:
            self.purchase_tree.heading(col, text=col)
            self.purchase_tree.column(col, width=100)
        
        self.purchase_tree.grid(row=len(fields)+1, column=0, columnspan=2, pady=10, sticky="nsew")
        
        # Configure grid weights
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(len(fields)+1, weight=1)
