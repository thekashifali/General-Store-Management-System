# seller_loans.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database import create_connection


class SellerLoans(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_loans()

    # =========================
    # UI SETUP
    # =========================
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        header = QLabel("Loan Payments")
        header.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50;")

        # ---------- PAYMENT BAR ----------
        pay_layout = QHBoxLayout()

        self.input_amount = QLineEdit()
        self.input_amount.setPlaceholderText("Payment Amount")

        btn_receive = QPushButton("Receive Payment")
        btn_receive.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        btn_receive.clicked.connect(self.receive_payment)

        pay_layout.addWidget(self.input_amount)
        pay_layout.addWidget(btn_receive)

        # ---------- TABLE ----------
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["#", "ID", "Customer", "Phone", "Balance", "Type"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet(self.table_style())

        main_layout.addWidget(header)
        main_layout.addLayout(pay_layout)
        main_layout.addWidget(self.table)

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
    # LOAD LOANS
    # =========================
    def load_loans(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT customer_id, name, phone, balance, type
            FROM customers
            WHERE type='loan'
        """)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for r, row in enumerate(rows):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(r + 1)))
            self.table.setItem(r, 1, QTableWidgetItem(str(row[0])))
            self.table.setItem(r, 2, QTableWidgetItem(row[1]))
            self.table.setItem(r, 3, QTableWidgetItem(row[2] or ""))
            self.table.setItem(r, 4, QTableWidgetItem(f"{row[3]:.2f}"))
            self.table.setItem(r, 5, QTableWidgetItem(row[4]))

    # =========================
    # RECEIVE PAYMENT
    # =========================
    def receive_payment(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Select a customer")
            return

        try:
            amount = float(self.input_amount.text())
            if amount <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Invalid", "Enter valid amount")
            return

        cid = self.table.item(row, 1).text()
        balance = float(self.table.item(row, 4).text())

        if amount > balance:
            QMessageBox.warning(self, "Amount Error", "Amount exceeds balance")
            return

        new_balance = balance - amount

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customers SET balance=%s WHERE customer_id=%s",
            (new_balance, cid)
        )
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Payment recorded")
        self.input_amount.clear()
        self.load_loans()
