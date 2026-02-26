# seller.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCloseEvent


from seller_pos import SellerPOS
from seller_customers import SellerCustomers
from seller_loans import SellerLoans
from seller_history import SellerHistory


class SellerDashboard(QWidget):
    logout_requested = pyqtSignal()
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.is_logging_out = False
        self.setWindowTitle("Seller Dashboard - Tajammal General Store")
        self.setFixedSize(1350, 700)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # =========================
        # SIDEBAR
        # =========================
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("background-color: #2c3e50; color: white;")

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(20, 40, 20, 40)
        side_layout.setSpacing(15)

        brand = QLabel("Muzammil\nSeller Panel")
        brand.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)

        nav_style = """
        QPushButton {
            background-color: transparent;
            color: #ecf0f1;
            text-align: left;
            padding: 12px 20px;
            font-size: 16px;
            border-radius: 8px;
            border: none;
        }
        QPushButton:hover {
            background-color: #34495e;
        }
        QPushButton:checked {
            background-color: #27ae60;
            color: white;
            font-weight: bold;
        }
        """

        self.btn_pos = QPushButton("  Sell Items")
        self.btn_customers = QPushButton("  Customers")
        self.btn_loans = QPushButton("  Loan Payments")
        self.btn_history = QPushButton("  Sales History")

        self.nav_buttons = [
            self.btn_pos,
            self.btn_customers,
            self.btn_loans,
            self.btn_history
        ]

        for btn in self.nav_buttons:
            btn.setCheckable(True)
            btn.setStyleSheet(nav_style)

        self.btn_pos.setChecked(True)

        # Logout button
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setStyleSheet("""
        QPushButton {
            background-color: #c0392b;
            color: white;
            padding: 12px;
            font-weight: bold;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #e74c3c;
        }
        """)
        self.btn_logout.clicked.connect(self.logout)

        # Sidebar layout
        side_layout.addWidget(brand)
        side_layout.addSpacing(40)
        side_layout.addWidget(self.btn_pos)
        side_layout.addWidget(self.btn_customers)
        side_layout.addWidget(self.btn_loans)
        side_layout.addWidget(self.btn_history)
        side_layout.addStretch()
        side_layout.addWidget(self.btn_logout)

        # =========================
        # CONTENT AREA
        # =========================
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #f5f6fa;")

        self.stack.addWidget(SellerPOS(self.username))
        self.stack.addWidget(SellerCustomers())
        self.stack.addWidget(SellerLoans())
        self.stack.addWidget(SellerHistory())

        # Navigation logic
        self.btn_pos.clicked.connect(lambda: self.switch_tab(0, self.btn_pos))
        self.btn_customers.clicked.connect(lambda: self.switch_tab(1, self.btn_customers))
        self.btn_loans.clicked.connect(lambda: self.switch_tab(2, self.btn_loans))
        self.btn_history.clicked.connect(lambda: self.switch_tab(3, self.btn_history))

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

    def switch_tab(self, index, active_btn):
        self.stack.setCurrentIndex(index)
        for btn in self.nav_buttons:
            btn.setChecked(False)
        active_btn.setChecked(True)

    def logout(self):
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()




    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to close the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()



