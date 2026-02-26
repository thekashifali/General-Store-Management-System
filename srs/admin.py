import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QStackedWidget, QFrame, QMessageBox, QApplication, QSizePolicy, QLineEdit, QGridLayout
)
from PyQt6.QtCore import Qt, QDate # QDate is required here
from PyQt6.QtGui import QFont, QCloseEvent
from PyQt6.QtCore import pyqtSignal


# --- IMPORT MODULES ---
from product_manager import ProductManager
from analytics_manager import AnalyticsManager  # <--- Make sure analytics_manager.py exists
from database import create_connection
from seller import SellerDashboard

class AdminDashboard(QWidget):
    logout_requested = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Dashboard - Tajammal General Store")
        self.setFixedSize(1350, 700)
        self.center_window()
        
        self.main_font = QFont("Segoe UI", 12)
        self.setFont(self.main_font)
        
        # --- NEW: CUSTOM SCROLLBAR STYLE (Blue Match) ---
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
            }
            /* VERTICAL SCROLLBAR */
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #2c3e50;  /* Sidebar Blue Color */
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #34495e;  /* Slightly Lighter on Hover */
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            /* HORIZONTAL SCROLLBAR */
            QScrollBar:horizontal {
                border: none;
                background: #f1f1f1;
                height: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #2c3e50;  /* Sidebar Blue Color */
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #34495e;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        # ------------------------------------------------
        
        self.is_logging_out = False 
        self.init_ui()

    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. SIDEBAR ---
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20, 40, 20, 40)
        sidebar_layout.setSpacing(15)
        
        brand_label = QLabel("Tajammal\nStore Admin")
        brand_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        nav_btn_style = """
            QPushButton {
                background-color: transparent; color: #ecf0f1; text-align: left;
                padding: 12px 20px; font-size: 16px; border-radius: 8px; border: none;
            }
            QPushButton:hover { background-color: #34495e; color: white; }
            QPushButton:checked { background-color: #27ae60; color: white; font-weight: bold; }
        """

        # --- NAVIGATION BUTTONS ---
        self.btn_dashboard = QPushButton("  Dashboard Overview")
        self.btn_dashboard.setCheckable(True)
        self.btn_dashboard.setChecked(True)
        self.btn_dashboard.setStyleSheet(nav_btn_style)
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))

        self.btn_inventory = QPushButton("  Inventory Management")
        self.btn_inventory.setCheckable(True)
        self.btn_inventory.setStyleSheet(nav_btn_style)
        self.btn_inventory.clicked.connect(lambda: self.switch_page(1))

        # 3. Analytics & Graphs (ADDED HERE, AFTER INVENTORY)
        self.btn_analytics = QPushButton("  Analytics & Graphs")
        self.btn_analytics.setCheckable(True)
        self.btn_analytics.setStyleSheet(nav_btn_style)
        self.btn_analytics.clicked.connect(lambda: self.switch_page(2))

        # [NEW] Settings Button
        self.btn_settings = QPushButton("  Settings / Password")
        self.btn_settings.setCheckable(True)
        self.btn_settings.setStyleSheet(nav_btn_style)
        self.btn_settings.clicked.connect(lambda: self.switch_page(3)) # Index 3

        # --- FIX: Add 'self.btn_analytics' in the correct order ---
        self.nav_buttons = [self.btn_dashboard, self.btn_inventory, self.btn_analytics, self.btn_settings]

        logout_btn_style = """
            QPushButton { background-color: #c0392b; color: white; padding: 12px; font-weight: bold; border-radius: 8px; }
            QPushButton:hover { background-color: #e74c3c; }
        """
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setStyleSheet(logout_btn_style)
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.clicked.connect(self.confirm_logout)

        sidebar_layout.addWidget(brand_label)
        sidebar_layout.addSpacing(40)
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_inventory)
        sidebar_layout.addWidget(self.btn_analytics) 
        sidebar_layout.addWidget(self.btn_settings) 
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_logout)
        sidebar.setLayout(sidebar_layout)

        # --- 2. CONTENT ---
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #f5f6fa;")

        self.page_dashboard = self.create_dashboard_page()
        self.page_inventory = self.create_inventory_page() 
        self.page_analytics = AnalyticsManager()
        self.page_settings = self.create_settings_page() # [NEW]

        self.content_stack.addWidget(self.page_dashboard)  # Index 0
        self.content_stack.addWidget(self.page_inventory)  # Index 1
        self.content_stack.addWidget(self.page_analytics) # Index 2
        self.content_stack.addWidget(self.page_settings)   # Index 3

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack)
        self.setLayout(main_layout)

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        if index == 0:
            self.refresh_dashboard_metrics()
        
    # =======================================================
    # CLOSE & LOGOUT LOGIC
    # =======================================================
    def closeEvent(self, event: QCloseEvent):
        if self.is_logging_out:
            event.accept()
            return

        reply = QMessageBox.question(
            self, 
            "Confirm Exit", 
            "Are you sure you want to close the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def confirm_logout(self):
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to log out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()

            

    # =======================================================
    # DASHBOARD LOGIC
    # =======================================================

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        # Logic to refresh specific pages when clicked
        if index == 0:
            self.refresh_dashboard_metrics()
        elif index == 2:
            self.page_analytics.refresh_charts()
    
    def refresh_dashboard_metrics(self):
        (invest, count, low, expired, 
         out_stock, profit, revenue) = self.get_dashboard_metrics()
        
        def set_text(card_obj, text):
            if hasattr(self, card_obj):
                getattr(self, card_obj).layout().itemAt(1).widget().setText(text)

        # Row 1
        set_text('card_investment', f"Rs. {invest:,.0f}")
        set_text('card_products', str(count))
        set_text('card_low_stock', str(low))
        set_text('card_expired', str(expired))
        
        # Row 2
        set_text('card_out_stock', str(out_stock))
        set_text('card_profit', f"Rs. {profit:,.0f}")
        set_text('card_revenue', f"Rs. {revenue:,.0f}")

    def get_dashboard_metrics(self):
        total_investment = 0.0
        total_products = 0
        low_stock_count = 0
        expired_count = 0  
        out_of_stock_count = 0
        est_profit = 0.0
        potential_revenue = 0.0

        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # 1. Total Investment
                cursor.execute("SELECT SUM(buying_price * stock) FROM products")
                result_invest = cursor.fetchone()
                if result_invest and result_invest[0]:
                    total_investment = float(result_invest[0])

                # 2. Total Products
                cursor.execute("SELECT COUNT(*) FROM products")
                result_count = cursor.fetchone()
                if result_count:
                    total_products = result_count[0]

                # 3. Low Stock
                cursor.execute("SELECT COUNT(*) FROM products WHERE stock < 10")
                result_low = cursor.fetchone()
                if result_low:
                    low_stock_count = result_low[0]

                # 4. EXPIRED ITEMS CHECK (NEW)
                today_str = QDate.currentDate().toString("yyyy-MM-dd")
                sql_expired = "SELECT COUNT(*) FROM products WHERE expiry_date IS NOT NULL AND expiry_date <= %s"
                cursor.execute(sql_expired, (today_str,))
                result_expired = cursor.fetchone()
                if result_expired:
                    expired_count = result_expired[0]

                # 5. OUT OF STOCK CHECK (NEW)
                cursor.execute("SELECT COUNT(*) FROM products WHERE stock <= 0")
                result_out = cursor.fetchone()
                if result_out:
                    out_of_stock_count = result_out[0]

                # 6 & 7. Revenue & Profit
                cursor.execute("SELECT SUM(selling_price * stock) FROM products")
                res_rev = cursor.fetchone()
                if res_rev and res_rev[0]:
                    potential_revenue = float(res_rev[0])
                
                est_profit = potential_revenue - total_investment
                    
            except Exception as e:
                print("Error calculating metrics:", e)
            finally:
                conn.close()
        
        # Return 4 values now instead of 3
        return total_investment, total_products, low_stock_count, expired_count, out_of_stock_count, est_profit, potential_revenue

    def create_dashboard_page(self):
        page = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        header = QLabel("Dashboard Overview")
        header.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50;")

        # Grid Layout
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(25)

        # Get all 8 values
        (invest, count, low, expired, 
         out_stock, profit, revenue) = self.get_dashboard_metrics()

        # --- ROW 1 ---
        self.card_investment = self.create_info_card("Total Investment", f"Rs. {invest:,.0f}", "#8e44ad")
        self.card_products = self.create_info_card("Total Products", str(count), "#27ae60")
        self.card_low_stock = self.create_info_card("Low Stock", str(low), "#e67e22")
        self.card_expired = self.create_info_card("Expired Items", str(expired), "#c0392b")
        
        # --- ROW 2 ---
        self.card_out_stock = self.create_info_card("Out of Stock", str(out_stock), "#c0392b")
        self.card_profit = self.create_info_card("Estimated Profit", f"Rs. {profit:,.0f}", "#27ae60")
        self.card_revenue = self.create_info_card("Potential Sales", f"Rs. {revenue:,.0f}", "#8e44ad")
        

        # Add Row 1
        self.cards_grid.addWidget(self.card_investment, 0, 0)
        self.cards_grid.addWidget(self.card_products, 0, 1)
        self.cards_grid.addWidget(self.card_low_stock, 0, 2)
        self.cards_grid.addWidget(self.card_expired, 0, 3)

        # Add Row 2
        self.cards_grid.addWidget(self.card_out_stock, 1, 0)
        self.cards_grid.addWidget(self.card_profit, 1, 1)
        self.cards_grid.addWidget(self.card_revenue, 1, 2) 

        main_layout.addWidget(header)
        main_layout.addLayout(self.cards_grid)
        main_layout.addStretch() 

        page.setLayout(main_layout)
        return page
    
    def create_info_card(self, title, value, bg_color):
        card = QFrame()
        card.setFixedHeight(160)
        card.setStyleSheet(f"background-color: {bg_color}; border-radius: 12px;")
        vbox = QVBoxLayout()
        
        l_t = QLabel(title)
        l_t.setFont(QFont("Segoe UI", 14))
        l_t.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        l_v = QLabel(value)
        l_v.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        l_v.setStyleSheet("color: white;")
        
        vbox.addWidget(l_t)
        vbox.addWidget(l_v)
        card.setLayout(vbox)
        return card

    # =======================================================
    # SETTINGS PAGE (CHANGE PASSWORD)
    # =======================================================
    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        
        header = QLabel("Account Settings")
        header.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        
        # --- PASSWORD FORM FRAME ---
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #dcdde1;")
        form_frame.setFixedWidth(500)
        
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)
        
        lbl_title = QLabel("Change Admin Password")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #34495e; margin-bottom: 10px; border: none;")
        
        self.input_curr_pass = QLineEdit()
        self.input_curr_pass.setPlaceholderText("Current Password")
        self.input_curr_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_curr_pass.setStyleSheet("padding: 10px; border: 1px solid #bdc3c7; border-radius: 6px;")
        
        self.input_new_pass = QLineEdit()
        self.input_new_pass.setPlaceholderText("New Password")
        self.input_new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_new_pass.setStyleSheet("padding: 10px; border: 1px solid #bdc3c7; border-radius: 6px;")
        
        self.input_confirm_pass = QLineEdit()
        self.input_confirm_pass.setPlaceholderText("Confirm New Password")
        self.input_confirm_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm_pass.setStyleSheet("padding: 10px; border: 1px solid #bdc3c7; border-radius: 6px;")
        
        btn_save = QPushButton("Update Password")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("background-color: #2980b9; color: white; padding: 10px; font-weight: bold; border-radius: 6px;")
        btn_save.clicked.connect(self.update_password_logic)

        form_layout.addWidget(lbl_title)
        form_layout.addWidget(self.input_curr_pass)
        form_layout.addWidget(self.input_new_pass)
        form_layout.addWidget(self.input_confirm_pass)
        form_layout.addSpacing(10)
        form_layout.addWidget(btn_save)
        form_frame.setLayout(form_layout)
        
        layout.addWidget(header)
        layout.addWidget(form_frame, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        
        page.setLayout(layout)
        return page

    def update_password_logic(self):
        curr = self.input_curr_pass.text()
        new = self.input_new_pass.text()
        conf = self.input_confirm_pass.text()

        if not curr or not new:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
        
        if new != conf:
            QMessageBox.warning(self, "Error", "New passwords do not match")
            return
            
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # 1. Verify Current Password for Admin
                # Note: Assuming username column holds the email
                cursor.execute("SELECT password FROM users WHERE username = 'Tajammal2025@gmail.com' AND role = 'admin'")
                result = cursor.fetchone()
                
                if result and result[0] == curr:
                    # 2. Update Password
                    cursor.execute("UPDATE users SET password = %s WHERE username = 'Tajammal2025@gmail.com'", (new,))
                    conn.commit()
                    QMessageBox.information(self, "Success", "Password updated successfully!")
                    self.input_curr_pass.clear()
                    self.input_new_pass.clear()
                    self.input_confirm_pass.clear()
                else:
                    QMessageBox.critical(self, "Error", "Current password is incorrect")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                conn.close()

    # --- INVENTORY PAGE ---
    def create_inventory_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.inventory_manager = ProductManager()
        layout.addWidget(self.inventory_manager)
        page.setLayout(layout)
        return page

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminDashboard()
    window.show()
    sys.exit(app.exec())