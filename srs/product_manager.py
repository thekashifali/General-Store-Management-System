import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, 
    QComboBox, QDateEdit, QDialog, QFormLayout, QDialogButtonBox, 
    QAbstractItemView, QApplication, QCheckBox, QMenu  # <--- Added QMenu here
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QColor
# Ensure this matches your actual file name for the database connection
from database import create_connection 

# ========================================================
# 1. THE POPUP FORM (Used for BOTH Add and Edit)
# ========================================================
class ProductFormDialog(QDialog):
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.setWindowTitle("Product Details")
        self.setFixedSize(450, 650) # Increased height for the extra field
        self.setStyleSheet("background-color: white;")
        
        self.product_data = product_data 
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        title = "Edit Product" if self.product_data else "Add New Product"
        lbl_header = QLabel(title)
        lbl_header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl_header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        lbl_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_header)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Styles
        input_style = "border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;"
        # Gray style for Read-Only fields
        read_only_style = "border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px; background-color: #ecf0f1; color: #2c3e50; font-weight: bold;"
        # Green style for Active Inputs
        highlight_style = "border: 2px solid #27ae60; border-radius: 5px; padding: 8px; font-size: 14px; background-color: #eafaf1;"

        # --- FIELDS ---
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("e.g. Rice (Chaawal)")
        self.input_name.setStyleSheet(input_style)
        
        self.combo_category = QComboBox()
        self.combo_category.addItems(["Select Category","General", "Grocery", "Drinks","Footwear", "Medicine", "Cosmetics", "Vegetables", "Fruits"])
        self.combo_category.setEditable(True)
        self.combo_category.setStyleSheet(input_style)
        
        self.combo_unit = QComboBox()
        self.combo_unit.addItems(["Select Unit","Piece", "Kg", "Liter","Packet", "Gram", "Box"])
        self.combo_unit.setStyleSheet(input_style)

        # 1. CURRENT STOCK
        self.input_stock = QLineEdit()
        self.input_stock.setStyleSheet(read_only_style if self.product_data else input_style)
        self.input_stock.setPlaceholderText("0.00")
        if self.product_data:
            self.input_stock.setReadOnly(True) 

        # 2. ADD NEW STOCK
        self.input_add_stock = QLineEdit()
        self.input_add_stock.setPlaceholderText("Qty to Add")
        self.input_add_stock.setStyleSheet(highlight_style)
        
        # 3. COST OF NEW STOCK (Input)
        self.input_total_cost = QLineEdit()
        self.input_total_cost.setPlaceholderText("Total cost of NEW items")
        self.input_total_cost.setStyleSheet(input_style)

        # 4. NEW UNIT COST (Display Only - Shows price of just the new batch)
        self.input_new_unit_cost = QLineEdit()
        self.input_new_unit_cost.setPlaceholderText("0.00")
        self.input_new_unit_cost.setStyleSheet(read_only_style)
        self.input_new_unit_cost.setReadOnly(True)

        # 5. FINAL AVG BUY PRICE (Auto-Calculated - This is saved to DB)
        self.input_buy = QLineEdit()
        self.input_buy.setPlaceholderText("Avg Price (Auto)")
        self.input_buy.setStyleSheet(read_only_style)
        self.input_buy.setReadOnly(True) 
        
        # 6. SELLING PRICE
        self.input_sell = QLineEdit()
        self.input_sell.setStyleSheet(input_style)
        
        # --- CONNECT CALCULATOR ---
        self.input_stock.textChanged.connect(self.calculate_weighted_average)      
        self.input_add_stock.textChanged.connect(self.calculate_weighted_average) 
        self.input_total_cost.textChanged.connect(self.calculate_weighted_average)

        # --- EXPIRY SECTION ---
        self.input_expiry = QDateEdit()
        self.input_expiry.setCalendarPopup(True)
        self.input_expiry.setDisplayFormat("yyyy-MM-dd")
        self.input_expiry.setDate(QDate.currentDate())
        self.input_expiry.setStyleSheet(input_style)
        self.input_expiry.setEnabled(False)

        self.chk_expiry = QCheckBox("Set Expiry Date")
        self.chk_expiry.setStyleSheet("font-size: 14px; color: #34495e;")
        self.chk_expiry.toggled.connect(self.input_expiry.setEnabled)

        expiry_layout = QHBoxLayout()
        expiry_layout.addWidget(self.chk_expiry)
        expiry_layout.addWidget(self.input_expiry)

        # --- LAYOUT SETUP ---
        form_layout.addRow("Product Name:", self.input_name)
        form_layout.addRow("Category:", self.combo_category)
        form_layout.addRow("Unit Type:", self.combo_unit)
        
        if self.product_data:
            # Edit Mode Layout
            form_layout.addRow("Current Stock:", self.input_stock)
            form_layout.addRow("Add New Stock:", self.input_add_stock)
            form_layout.addRow("Cost of New Stock:", self.input_total_cost)
            # This is the NEW field you asked for
            form_layout.addRow("New Stock Unit Cost:", self.input_new_unit_cost)
            form_layout.addRow("Final Avg Cost:", self.input_buy)
        else:
            # Add Mode Layout
            form_layout.addRow("Initial Stock:", self.input_stock)
            self.input_add_stock.hide() 
            self.input_new_unit_cost.hide() # Hide in Add Mode
            form_layout.addRow("Total Buying Cost:", self.input_total_cost)
            form_layout.addRow("Buy Price (Per Unit):", self.input_buy)

        form_layout.addRow("Sell Price :", self.input_sell)
        form_layout.addRow("Expiry:", expiry_layout)

        layout.addLayout(form_layout)
        layout.addStretch()

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.validate_data)
        btn_box.rejected.connect(self.reject)
        
        btn_box.button(QDialogButtonBox.StandardButton.Save).setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        btn_box.button(QDialogButtonBox.StandardButton.Cancel).setStyleSheet("background-color: #c0392b; color: white; padding: 10px;")
        
        layout.addWidget(btn_box)
        self.setLayout(layout)

        if self.product_data:
            self.fill_data()

    def calculate_weighted_average(self):
        try:
            # --- 1. Get New Data (Inputs) ---
            new_qty_text = "0"
            if self.product_data:
                new_qty_text = self.input_add_stock.text() or "0"
            else:
                new_qty_text = self.input_stock.text() or "0"
            
            new_cost_text = self.input_total_cost.text() or "0"

            new_qty = float(new_qty_text)
            new_total_cost = float(new_cost_text)

            # --- 2. Calculate "New Stock Unit Cost" (Specific to this batch) ---
            if new_qty > 0:
                specific_unit_cost = new_total_cost / new_qty
                self.input_new_unit_cost.setText(f"{specific_unit_cost:.2f}")
            else:
                self.input_new_unit_cost.setText("0.00")

            # --- 3. Calculate "Weighted Average" (Old + New) ---
            old_qty = 0.0
            old_price = 0.0
            
            if self.product_data:
                # Fetch old data from UI/DB
                old_qty_text = self.input_stock.text() or "0"
                old_qty = float(old_qty_text)
                old_price = float(self.product_data[4]) # Original buying price

            # Total Value Formula
            old_total_value = old_qty * old_price
            grand_total_value = old_total_value + new_total_cost
            grand_total_qty = old_qty + new_qty

            if grand_total_qty > 0:
                average_price = grand_total_value / grand_total_qty
                self.input_buy.setText(f"{average_price:.2f}")
            else:
                self.input_buy.setText("0.00")

        except ValueError:
            pass

    def fill_data(self):
        self.input_name.setText(self.product_data[1])
        self.combo_category.setCurrentText(self.product_data[2])
        self.combo_unit.setCurrentText(self.product_data[3])
        
        # Format existing data to 2 decimals
        unit_buy_price = f"{float(self.product_data[4]):.2f}"
        selling_price = f"{float(self.product_data[5]):.2f}"
        current_stock = f"{float(self.product_data[6]):.2f}"

        self.input_buy.setText(unit_buy_price)
        self.input_sell.setText(selling_price)
        self.input_stock.setText(current_stock) 
        
        expiry_val = str(self.product_data[7])
        if expiry_val and expiry_val.lower() != "none" and expiry_val.strip() != "":
            self.chk_expiry.setChecked(True)
            self.input_expiry.setEnabled(True)
            try:
                self.input_expiry.setDate(QDate.fromString(expiry_val, "yyyy-MM-dd"))
            except:
                pass
        else:
            self.chk_expiry.setChecked(False)
            self.input_expiry.setEnabled(False)

    def validate_data(self):
        # 1. Validate Name
        if not self.input_name.text().strip():
            QMessageBox.warning(self, "Input Error", "Product Name is required.")
            return

        # 2. Validate Category
        # Check if the user left it on "Select Category" or left it empty
        current_cat = self.combo_category.currentText()
        if current_cat == "Select Category" or current_cat.strip() == "":
            QMessageBox.warning(self, "Input Error", "Please select a valid Category.")
            self.combo_category.setFocus() # Move focus to the box so user sees it
            return

        # 3. Validate Unit
        # Check if the user left it on "Select Unit" or left it empty
        current_unit = self.combo_unit.currentText()
        if current_unit == "Select Unit" or current_unit.strip() == "":
            QMessageBox.warning(self, "Input Error", "Please select a valid Unit Type.")
            self.combo_unit.setFocus()
            return

        # 4. Validate Prices
        if not self.input_buy.text() or not self.input_sell.text():
            QMessageBox.warning(self, "Input Error", "Prices are required.")
            return
            
        # If all checks pass, close the dialog and save
        self.accept()

    def get_data(self):
        expiry_val = None
        if self.chk_expiry.isChecked():
            expiry_val = self.input_expiry.date().toString("yyyy-MM-dd")

        current_stock_val = 0.0
        try:
            current_stock_val = float(self.input_stock.text())
        except: pass

        add_stock_val = 0.0
        try:
            if self.product_data: 
                add_stock_val = float(self.input_add_stock.text())
        except: pass

        final_stock = current_stock_val + add_stock_val

        return {
            "name": self.input_name.text(),
            "category": self.combo_category.currentText(),
            "unit": self.combo_unit.currentText(),
            "buy": self.input_buy.text(), # Sends the Weighted Average
            "sell": self.input_sell.text(),
            "stock": str(final_stock), 
            "expiry": expiry_val
        }


# ========================================================
# 2. THE MAIN MANAGER (Table + Buttons)
# ========================================================
class ProductManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- TOOLBAR ---
        toolbar = QHBoxLayout()
        
        lbl_search = QLabel("Search:")
        lbl_search.setFont(QFont("Segoe UI", 12))
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Search items...")
        self.input_search.setStyleSheet("border: 1px solid #bdc3c7; padding: 6px; border-radius: 4px;")
        self.input_search.textChanged.connect(self.search_item)

        btn_add = self.create_button(" + Add Product ", "#27ae60", self.open_add_dialog)
        btn_edit = self.create_button(" Edit Selected ", "#2980b9", self.open_edit_dialog)
        btn_delete = self.create_button(" Delete ", "#c0392b", self.delete_item)
        btn_refresh = self.create_button(" Refresh ", "#7f8c8d", self.load_data)

        toolbar.addWidget(lbl_search)
        toolbar.addWidget(self.input_search)
        toolbar.addSpacing(20)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_edit)
        toolbar.addWidget(btn_delete)
        toolbar.addWidget(btn_refresh)

        # --- TABLE ---
        self.table = QTableWidget()
        # --- NEW: ENABLE RIGHT CLICK MENU ---
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Unit", "Buy Price", "Sell Price", "Stock", "Expiry"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) 
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) 
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f2f2f2;
                border: 1px solid #dcdde1;
                font-size: 14px;
                gridline-color: #ecf0f1;
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
            QTableCornerButton::section {
                background-color: #2c3e50;
                border: 1px solid #34495e;
            }
        """)

        layout.addLayout(toolbar)
        layout.addWidget(self.table)
        self.setLayout(layout)
        
        self.load_data()

    def create_button(self, text, color, func):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; padding: 8px; border-radius: 4px;")
        btn.clicked.connect(func)
        return btn

    # --- DATABASE FUNCTIONS ---
    def load_data(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # --- LOGIC UPDATE: SORT LOW STOCK TO TOP ---
                # "stock < 10 DESC" puts True (1) before False (0)
                sql = """
                    SELECT * FROM products 
                    ORDER BY (stock < 10) DESC, product_id DESC
                """
                cursor.execute(sql)
                rows = cursor.fetchall()
                self.populate_table(rows)
            finally:
                conn.close()

    def search_item(self):
        text = self.input_search.text().strip()
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                wildcard = f"%{text}%"
                
                # 1. Get Today's Date safely
                today_str = QDate.currentDate().toString("yyyy-MM-dd")
                
                # 2. CHECK FOR 'exp'
                if "exp" in text.lower():
                    # --- FIXED QUERY: Removed "!= ''" checks ---
                    # Only checking IS NOT NULL and the date comparison
                    sql = """
                        SELECT * FROM products 
                        WHERE name LIKE %s 
                        OR category LIKE %s 
                        OR (expiry_date IS NOT NULL 
                            AND expiry_date <= %s)
                        ORDER BY (stock < 10) DESC, product_id DESC
                    """
                    # 3 params required
                    params = (wildcard, wildcard, today_str)
                    print("Search Mode: EXPIRED (3 params)")
                
                else:
                    # --- Normal Search ---
                    sql = """
                        SELECT * FROM products 
                        WHERE name LIKE %s OR category LIKE %s 
                        ORDER BY (stock < 10) DESC, product_id DESC
                    """
                    # 2 params required
                    params = (wildcard, wildcard)
                    print("Search Mode: NORMAL (2 params)")
                
                # 3. Execute
                cursor.execute(sql, params)
                
                rows = cursor.fetchall()
                self.populate_table(rows)
            
            except Exception as e:
                print(f"CRITICAL SEARCH ERROR: {e}")
            finally:
                conn.close()
    def populate_table(self, rows):
        """ Fills the table. If date is passed, column shows 'Expired' in Red. """
        self.table.setRowCount(0)
        low_stock_limit = 10.0 
        today = QDate.currentDate()

        for r, row in enumerate(rows):
            self.table.insertRow(r)
            
            # --- 1. CHECK STOCK & EXPIRY ---
            try:
                current_stock = float(row[6]) # Col 6 is Stock
            except:
                current_stock = 0.0
            
            expiry_str = str(row[7]) # Col 7 is Expiry
            
            is_low_stock = current_stock < low_stock_limit
            is_expired = False

            # Check Date Logic
            if expiry_str and expiry_str.lower() != "none" and expiry_str.strip() != "":
                try:
                    exp_date = QDate.fromString(expiry_str, "yyyy-MM-dd")
                    if exp_date <= today:
                        is_expired = True
                except:
                    pass

            # --- 2. FILL CELLS ---
            for c, data in enumerate(row):
                val = ""
                if data is not None:
                    # Format numbers for Price/Stock
                    if c in [4, 5, 6]: 
                        try:
                            val = f"{float(data):.2f}"
                        except:
                            val = str(data)
                    else:
                        val = str(data)
                
                # *** LOGIC CHANGE: IF EXPIRED, SHOW ONLY "Expired" ***
                if c == 7 and is_expired:
                    val = "Expired" 

                item = QTableWidgetItem(val)
                
                # --- 3. COLORS (Red Text) ---
                font = item.font()
                
                if is_expired:
                    # Expired = Red Text + Bold
                    item.setForeground(QColor("red")) 
                    font.setBold(True)
                    item.setFont(font)
                
                elif is_low_stock:
                    # Low Stock = Red Text
                    item.setForeground(QColor("red"))
                    item.setFont(font)

                self.table.setItem(r, c, item)

    # --- ADD ---
    def open_add_dialog(self):
        dialog = ProductFormDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                sql = "INSERT INTO products (name, category, unit, buying_price, selling_price, stock, expiry_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (data['name'], data['category'], data['unit'], data['buy'], data['sell'], data['stock'], data['expiry']))
                conn.commit()
                conn.close()
                self.load_data()
                QMessageBox.information(self, "Success", "Product Added!")

    # --- EDIT ---
    def open_edit_dialog(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Item", "Please click a row in the table to edit.")
            return
        
        # --- NEW LOGIC: BLOCK EDIT IF EXPIRED ---
        # Column 7 is the Expiry Date / Status column
        expiry_status = self.table.item(row, 7).text()
        
        if "Expired" in expiry_status:
            QMessageBox.warning(self, "Action Denied", "This item is EXPIRED.\n\nYou cannot edit expired stock.\nPlease delete this item and add the fresh stock as a new product.")
            return

        p_id = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        cat = self.table.item(row, 2).text()
        unit = self.table.item(row, 3).text()
        buy = self.table.item(row, 4).text()
        sell = self.table.item(row, 5).text()
        stock = self.table.item(row, 6).text()
        expiry = self.table.item(row, 7).text()

        data_tuple = (p_id, name, cat, unit, buy, sell, stock, expiry)

        dialog = ProductFormDialog(self, product_data=data_tuple)
        if dialog.exec():
            new_data = dialog.get_data()
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                sql = "UPDATE products SET name=%s, category=%s, unit=%s, buying_price=%s, selling_price=%s, stock=%s, expiry_date=%s WHERE product_id=%s"
                cursor.execute(sql, (new_data['name'], new_data['category'], new_data['unit'], new_data['buy'], new_data['sell'], new_data['stock'], new_data['expiry'], p_id))
                conn.commit()
                conn.close()
                self.load_data()
                QMessageBox.information(self, "Success", "Product Updated!")

    # --- DELETE ---
    def delete_item(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Item", "Please click a row in the table to delete.")
            return
        
        p_id = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()

        confirm = QMessageBox.question(self, "Confirm", f"Delete '{name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE product_id=%s", (p_id,))
                conn.commit()
                conn.close()
                self.load_data()

    # ==========================================
    #  RIGHT CLICK CONTEXT MENU LOGIC
    # ==========================================
    def show_context_menu(self, position):
        # 1. Get the row where user clicked
        index = self.table.indexAt(position)
        if not index.isValid():
            return
        
        # 2. Create the Menu
        from PyQt6.QtWidgets import QMenu # Ensure QMenu is imported
        menu = QMenu()
        
        # 3. Add Actions
        action_view = menu.addAction("View Full Details")
        action_edit = menu.addAction("Edit This Item")
        action_delete = menu.addAction("Delete This Item")
        
        # 4. Show Menu and Capture Click
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        # 5. Handle Clicks
        if action == action_view:
            self.show_full_details(index.row())
        elif action == action_edit:
            self.open_edit_dialog() # Reuses your existing edit function
        elif action == action_delete:
            self.delete_item()      # Reuses your existing delete function

    def show_full_details(self, row):
        # Extract data from the row
        p_id = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        category = self.table.item(row, 2).text()
        unit = self.table.item(row, 3).text()
        buy = self.table.item(row, 4).text()
        sell = self.table.item(row, 5).text()
        stock = self.table.item(row, 6).text()
        expiry = self.table.item(row, 7).text()

        # Create a detailed message
        info_text = (
            f"<b>Product Name:</b> <span style='font-size:14pt; color:#2c3e50;'>{name}</span><br><br>"
            f"<b>Category:</b> {category}<br>"
            f"<b>Stock Status:</b> {stock} {unit}<br>"
            f"<b>Buy Price:</b> {buy}<br>"
            f"<b>Sell Price:</b> {sell}<br>"
            f"<b>Expiry Date:</b> {expiry}<br>"
            f"<b>Product ID:</b> {p_id}"
        )

        # Show Popup
        msg = QMessageBox(self)
        msg.setWindowTitle("Product Details")
        msg.setTextFormat(Qt.TextFormat.RichText) # Enable HTML styling
        msg.setText(info_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductManager()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec())