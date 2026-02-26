# seller_customers.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QComboBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database import create_connection


class SellerCustomers(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_customers()

    # =========================
    # UI SETUP
    # =========================
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        header = QLabel("Customers")
        header.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50;")

        # ---------- FORM ----------
        form_layout = QHBoxLayout()
        form_layout.setSpacing(15)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Customer Name")

        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Phone")

        self.combo_type = QComboBox()
        self.combo_type.addItems(["cash", "loan"])

        btn_add = QPushButton("Add Customer")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        btn_add.clicked.connect(self.add_customer)

        form_layout.addWidget(self.input_name)
        form_layout.addWidget(self.input_phone)
        form_layout.addWidget(self.combo_type)
        form_layout.addWidget(btn_add)

        # ---------- TABLE ----------
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Phone", "Type"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.table.setStyleSheet(self.table_style())

        btn_delete = QPushButton("Delete Selected")
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        btn_delete.clicked.connect(self.delete_customer)

        main_layout.addWidget(header)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(btn_delete, alignment=Qt.AlignmentFlag.AlignRight)

    # =========================
    # TABLE STYLE
    # =========================
    def table_style(self):
        return """
        QTableWidget {
            background-color: white;
            border: 1px solid #dcdde1;
            font-size: 14px;
        }
        QHeaderView::section {
            background-color: #2c3e50;
            color: white;
            padding: 8px;
            font-weight: bold;
        }
        QTableWidget::item:selected {
            background-color: #2980b9;
            color: white;
        }
        """

    # =========================
    # LOAD CUSTOMERS
    # =========================
    def load_customers(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id, name, phone, type FROM customers")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for r, row in enumerate(rows):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(r, 1, QTableWidgetItem(row[1]))
            self.table.setItem(r, 2, QTableWidgetItem(row[2] or ""))
            self.table.setItem(r, 3, QTableWidgetItem(row[3]))

    # =========================
    # ADD CUSTOMER
    # =========================
    def add_customer(self):
        name = self.input_name.text().strip()
        phone = self.input_phone.text().strip()
        ctype = self.combo_type.currentText()

        if not name:
            QMessageBox.warning(self, "Input Error", "Customer name required")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO customers (name, phone, type) VALUES (%s,%s,%s)",
            (name, phone, ctype)
        )
        conn.commit()
        conn.close()

        self.input_name.clear()
        self.input_phone.clear()
        self.load_customers()

    # =========================
    # DELETE CUSTOMER
    # =========================
    def delete_customer(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Select a customer")
            return

        cid = self.table.item(row, 1).text()
        name = self.table.item(row, 2).text()

        confirm = QMessageBox.question(
            self, "Confirm", f"Delete {name}?"
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE customer_id=%s", (cid,))
        conn.commit()
        conn.close()

        self.load_customers()
