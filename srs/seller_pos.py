from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QComboBox, QHeaderView, QCheckBox
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont, QTextDocument, QPageSize
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from database import create_connection

class SellerPOS(QWidget):
    def __init__(self, seller_username):
        super().__init__()
        self.seller = seller_username
        self.cart = []
        self.init_ui()
        self.load_products()

    # =========================
    # UI SETUP
    # =========================
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # =========================
        # LEFT SIDE (PRODUCTS)
        # =========================
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)

        header = QLabel("Sell Items")
        header.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search product (Name or Category)...")
        self.search_input.textChanged.connect(self.load_products)
        self.search_input.setStyleSheet(
            "padding:8px;border:1px solid #bdc3c7;border-radius:6px;"
        )

        self.products_table = QTableWidget(0, 6)
        self.products_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Category", "Unit", "Price", "Stock"]
        )

        self.products_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.products_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.products_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.products_table.cellDoubleClicked.connect(self.add_to_cart)
        self.products_table.setStyleSheet(self.table_style())

        left_layout.addWidget(header)
        left_layout.addWidget(self.search_input)
        left_layout.addWidget(self.products_table)

        # =========================
        # RIGHT SIDE (CART)
        # =========================
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        cart_lbl = QLabel("Cart")
        cart_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))

        self.cart_table = QTableWidget(0, 5)
        self.cart_table.setHorizontalHeaderLabels(
            ["Name", "Qty", "Price", "Total", "Remove"]
        )
        self.cart_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.cart_table.cellDoubleClicked.connect(self.handle_qty_edit)
        self.cart_table.cellChanged.connect(self.qty_changed)
        
        self.cart_table.setStyleSheet(self.table_style())

        self.cart_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.cart_table.customContextMenuRequested.connect(self.show_cart_details)

        self.payment_type = QComboBox()
        self.payment_type.addItems(["Cash", "Loan"])
        self.payment_type.currentTextChanged.connect(self.toggle_customer)

        self.customer_box = QComboBox()
        self.customer_box.setEnabled(False)

        self.total_label = QLabel("Total: Rs 0.00")
        self.total_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # --- PRINT CHECKBOX ---
        self.chk_print = QCheckBox("Print Invoice")
        self.chk_print.setChecked(False) # Default unchecked
        self.chk_print.setFont(QFont("Segoe UI", 12))
        self.chk_print.setCursor(Qt.CursorShape.PointingHandCursor)

        # --- COMPLETE BUTTON ---
        btn_complete = QPushButton("Complete Sale")
        btn_complete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_complete.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: white;
                padding: 12px;
                font-weight: bold;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #004080;
            }
        """)
        btn_complete.clicked.connect(self.complete_sale)

        # Add items to Right Layout
        right_layout.addWidget(cart_lbl)
        right_layout.addWidget(self.cart_table)
        right_layout.addWidget(QLabel("Payment Type"))
        right_layout.addWidget(self.payment_type)
        right_layout.addWidget(QLabel("Customer (Loan Only)"))
        right_layout.addWidget(self.customer_box)
        right_layout.addWidget(self.total_label)
        
        right_layout.addWidget(self.chk_print) # Checkbox added here
        right_layout.addWidget(btn_complete)   # Button added here

        main_layout.addLayout(left_layout, 65)
        main_layout.addLayout(right_layout, 35)

    # =========================
    # TABLE STYLE
    # =========================
    def table_style(self):
        return """
        QTableWidget {
            background-color: white;
            alternate-background-color: #f2f2f2;
            border: 1px solid #dcdde1;
            font-size: 14px;
        }
        QHeaderView::section {
            background-color: #2c3e50;
            color: white;
            padding: 8px;
            font-weight: bold;
            border: 1px solid #34495e;
        }
        QTableWidget::item:selected {
            background-color: #2980b9;
            color: white;
        }
        """

    # =========================
    # LOAD PRODUCTS
    # =========================
    def load_products(self):
        text = self.search_input.text()
        conn = create_connection()
        if not conn:
            return

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT product_id, name, category, unit, selling_price, stock
            FROM products
            WHERE name LIKE %s OR category LIKE %s
            """,
            (f"%{text}%", f"%{text}%")
        )

        rows = cursor.fetchall()
        conn.close()

        self.products_table.setRowCount(0)

        for r, row in enumerate(rows):
            self.products_table.insertRow(r)
            self.products_table.setItem(r, 0, QTableWidgetItem(str(row[0])))
            self.products_table.setItem(r, 1, QTableWidgetItem(row[1]))
            self.products_table.setItem(r, 2, QTableWidgetItem(row[2]))
            self.products_table.setItem(r, 3, QTableWidgetItem(row[3]))
            self.products_table.setItem(r, 4, QTableWidgetItem(f"{row[4]:.2f}"))
            self.products_table.setItem(r, 5, QTableWidgetItem(f"{row[5]:.2f}"))

    # =========================
    # CART LOGIC
    # =========================
    def add_to_cart(self, row, col):
        # Get data from the clicked row in products_table
        pid = int(self.products_table.item(row, 0).text())
        name = self.products_table.item(row, 1).text()
        unit = self.products_table.item(row, 3).text()
        price = float(self.products_table.item(row, 4).text())
        stock = float(self.products_table.item(row, 5).text())

        # Check 1: Is stock completely empty?
        if stock <= 0:
            QMessageBox.warning(self, "Out of Stock", "Item out of stock")
            return

        # Check 2: Is item already in the cart?
        for item in self.cart:
            if item["pid"] == pid:
                QMessageBox.warning(self, "Already Added", "Item already in cart")
                return

        # Check 3: Logic Check - Can we add the default 1 unit?
        # Since double-clicking adds 1 unit by default, we must ensure we have at least 1.
        # If you have 0.7 stock, you cannot add 1.
        if stock < 1:
             QMessageBox.warning(self, "Low Stock", f"Insufficient Stock!\nYou only have {stock} available, but are trying to add 1.")
             return

        # If all checks pass, add to cart with default qty = 1.0
        self.cart.append({
            "pid": pid,
            "name": name,
            "qty": 1.0,
            "unit": unit,
            "price": price,
            "stock": stock
        })

        self.refresh_cart()

    def refresh_cart(self):
        self.cart_table.blockSignals(True)
        self.cart_table.setRowCount(0)
        total_sum = 0

        for r, item in enumerate(self.cart):
            self.cart_table.insertRow(r)
            
            # --- 0: Name ---
            name_item = QTableWidgetItem(item["name"])
            name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.cart_table.setItem(r, 0, name_item)
            
            # --- 1: Qty ---
            qty_item = QTableWidgetItem(f"{item['qty']:.1f} {item['unit']}")
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(r, 1, qty_item)
            
            # --- 2: Price ---
            price_item = QTableWidgetItem(f"{item['price']:.2f}")
            price_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.cart_table.setItem(r, 2, price_item)
            
            # --- 3: Total ---
            row_total = item["qty"] * item["price"]
            total_item = QTableWidgetItem(f"{row_total:.2f}")
            total_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.cart_table.setItem(r, 3, total_item)
            
            total_sum += row_total

            # --- 4: Remove Button ---
            btn = QPushButton("X")
            btn.setFixedSize(30, 22)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; border-radius: 4px;")
            btn.clicked.connect(lambda _, i=r: self.remove_item(i))

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(6, 4, 6, 4)
            layout.addWidget(btn)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cart_table.setCellWidget(r, 4, container)

        self.cart_table.blockSignals(False)
        self.total_label.setText(f"Total: Rs {total_sum:.2f}")

    # =========================
    # EDIT LOGIC
    # =========================
    def handle_qty_edit(self, row, col):
        if col == 1:
            item = self.cart_table.item(row, col)
            if item:
                self.cart_table.blockSignals(True)
                text = item.text().split(' ')[0]
                item.setText(text)
                self.cart_table.blockSignals(False)
                self.cart_table.editItem(item)

    # =========================
    # EDIT LOGIC (SMART INTEGERS)
    # =========================
    def qty_changed(self, row, col):
        """Validate input: Enforce Integers for Packets/Pieces, allow Decimals for Kg/Ltr"""
        if col != 1:
            return

        item = self.cart_table.item(row, col)
        if not item: return

        # Get the product details from the cart list
        cart_item = self.cart[row]
        unit = cart_item['unit'].lower() # e.g. 'kg', 'piece', 'packet'

        try:
            text_val = item.text().strip()
            
            # --- 1. DEFINE UNITS THAT ALLOW DECIMALS ---
            decimal_units = ['kg', 'g', 'gram', 'ltr', 'liter', 'm', 'meter']
            
            # --- 2. CHECK LOGIC ---
            if unit in decimal_units:
                # Allow decimals (e.g., 1.5 kg)
                value = float(text_val)
            else:
                # Enforce Integer for Packets, Pieces, etc.
                # First convert to float to catch inputs like "2.0"
                f_val = float(text_val)
                
                # Check if it has a decimal part (e.g., 2.4)
                if not f_val.is_integer():
                    QMessageBox.warning(self, "Invalid Quantity", f"'{cart_item['unit']}' cannot be decimal.\nPlease enter a whole number (e.g., 1, 2, 5).")
                    raise ValueError("Integer required")
                
                value = int(f_val)

            # --- 3. STOCK & POSITIVE CHECK ---
            if value <= 0:
                QMessageBox.warning(self, "Error", "Quantity must be positive")
                raise ValueError("Positive required")
            
            if value > cart_item["stock"]:
                QMessageBox.warning(self, "Stock Error", f"Only {cart_item['stock']} {unit} available!")
                raise ValueError("Out of stock")

            # Update the cart data
            self.cart[row]["qty"] = value

        except ValueError:
            # If invalid, this 'pass' relies on refresh_cart() to reset the cell to the old value
            pass 
        
        # Refresh table to format text correctly (e.g., add 'kg' or 'Piece' back to string)
        self.refresh_cart()

    def remove_item(self, index):
        self.cart.pop(index)
        self.refresh_cart()

    def show_cart_details(self, pos):
        row = self.cart_table.rowAt(pos.y())
        if row < 0: return
        item = self.cart[row]
        details = (
            f"Product Name : {item['name']}\n"
            f"Quantity     : {item['qty']:.1f} {item['unit']}\n"
            f"Unit Price   : Rs {item['price']:.2f}\n"
            f"Total Price  : Rs {item['qty'] * item['price']:.2f}\n"
            f"Stock Left   : {item['stock']:.2f} {item['unit']}"
        )
        QMessageBox.information(self, "Cart Item Details", details)

    # =========================
    # PAYMENT LOGIC
    # =========================
    def toggle_customer(self, text):
        self.customer_box.setEnabled(text.lower() == "loan")
        if text.lower() == "loan":
            self.load_customers()
        else:
            self.customer_box.clear()

    def load_customers(self):
        self.customer_box.clear()
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id, name FROM customers WHERE type='loan'")
        for cid, name in cursor.fetchall():
            self.customer_box.addItem(name, cid)
        conn.close()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_products()

    # =========================
    # COMPLETE SALE
    # =========================
    def complete_sale(self):
        if not self.cart:
            QMessageBox.warning(self, "Empty Cart", "No items in cart")
            return

        total = sum(i["qty"] * i["price"] for i in self.cart)
        payment = self.payment_type.currentText().lower()
        customer_id = None
        customer_name = "Walk-in Customer"
        paid = total

        if payment == "loan":
            if self.customer_box.currentIndex() < 0:
                QMessageBox.warning(self, "Customer", "Select loan customer")
                return
            customer_id = self.customer_box.currentData()
            customer_name = self.customer_box.currentText()
            paid = 0

        # --- DB Transaction ---
        conn = create_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sales (seller_username, customer_id, total_amount, paid_amount, payment_type)
                VALUES (%s,%s,%s,%s,%s)
            """, (self.seller, customer_id, total, paid, payment))

            sale_id = cursor.lastrowid

            for item in self.cart:
                cursor.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price)
                    VALUES (%s,%s,%s,%s,%s)
                """, (
                    sale_id, item["pid"], item["qty"], item["price"],
                    item["qty"] * item["price"]
                ))
                cursor.execute(
                    "UPDATE products SET stock = stock - %s WHERE product_id = %s",
                    (item["qty"], item["pid"])
                )

            conn.commit()
            
            # =======================================================
            # ✅ CHECKBOX LOGIC
            # =======================================================
            # If Checked: Print. If Unchecked: Do nothing.
            if self.chk_print.isChecked():
                # Pass a copy of the cart list because we are about to clear it
                self.generate_invoice(sale_id, customer_name, list(self.cart), total)

            # =======================================================
            # Cleanup
            self.cart.clear()
            self.refresh_cart()
            self.load_products()
            QMessageBox.information(self, "Success", "Sale completed successfully")

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Transaction failed: {str(e)}")
        finally:
            conn.close()

    # =========================
    # INVOICE PRINTING
    # =========================
    def generate_invoice(self, sale_id, cust_name, cart_items, total):
        date_str = QDateTime.currentDateTime().toString("dd-MM-yyyy HH:mm")
        
        rows_html = ""
        total_qty = 0
        for i, item in enumerate(cart_items, 1):
            row_price = item['qty'] * item['price']
            total_qty += item['qty']
            rows_html += f"""
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 8px; text-align: center;">{i}</td>
                <td style="padding: 8px;">{item['name']}</td>
                <td style="padding: 8px; text-align: center;">{item['unit']}</td>
                <td style="padding: 8px; text-align: center;">{item['qty']:.1f}</td>
                <td style="padding: 8px; text-align: right;">{item['price']:.0f}</td>
                <td style="padding: 8px; text-align: center;">0</td>
                <td style="padding: 8px; text-align: right;">{row_price:.0f}</td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #000; margin: 20px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                .header {{ margin-bottom: 20px; }}
                .company-name {{ font-size: 28px; font-weight: bold; color: #000; }}
                .invoice-title {{ font-size: 28px; font-weight: bold; color: #003366; text-align: right; }}
                .meta-info {{ font-size: 14px; margin-top: 5px; }}
                
                .items-table {{ margin-top: 20px; border: 1px solid #000; }}
                .items-table th {{ 
                    background-color: #003366; 
                    color: white; 
                    padding: 10px; 
                    text-align: left;
                    font-size: 14px;
                }}
                .items-table td {{ font-size: 14px; color: #000; }}
                
                .summary {{ float: right; margin-top: 20px; width: 300px; }}
                .summary td {{ padding: 5px; font-size: 16px; font-weight: bold; }}
                .total-row {{ color: #003366; font-size: 18px; }}
                
                .footer {{ 
                    margin-top: 50px; 
                    text-align: center; 
                    font-size: 12px; 
                    border-top: 1px solid #ccc; 
                    padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <table class="header">
                <tr>
                    <td width="60%">
                        <div class="company-name">Tajammal General Store</div>
                        <div class="meta-info"><b>Address:</b> Tanki, Jung Road, City</div>
                        <div class="meta-info"><b>Phone:</b> 0322-1234567</div>
                    </td>
                    <td width="40%" valign="top">
                        <div class="invoice-title">INVOICE</div>
                        <div style="text-align: right; margin-top: 10px;">
                            <b>Invoice #:</b> {sale_id}<br>
                            <b>Date:</b> {date_str}
                        </div>
                    </td>
                </tr>
            </table>

            <div style="margin-top: 20px; border-top: 2px solid #003366; padding-top: 10px;">
                <b>Bill To:</b> {cust_name}
            </div>

            <table class="items-table">
                <thead>
                    <tr>
                        <th width="5%">#</th>
                        <th width="35%">Item</th>
                        <th width="10%">Unit</th>
                        <th width="10%">Qty</th>
                        <th width="15%" style="text-align: right;">Price</th>
                        <th width="10%" style="text-align: center;">Disc</th>
                        <th width="15%" style="text-align: right;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <table class="summary">
                <tr>
                    <td align="right">Total Qty:</td>
                    <td align="right">{total_qty:.1f}</td>
                </tr>
                <tr class="total-row">
                    <td align="right">Grand Total:</td>
                    <td align="right">Rs {total:.0f}</td>
                </tr>
            </table>

            <div style="clear: both;"></div>

            <div class="footer">
                Thank you for your business!<br>
                Software Developed by Muzammil
            </div>
        </body>
        </html>
        """

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setFullPage(True)
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            doc = QTextDocument()
            doc.setHtml(html)
            doc.print(printer)