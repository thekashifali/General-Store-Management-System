import sys
import os
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QMessageBox, QApplication)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QFont, QScreen
# Ensure database.py is in the same folder and configured correctly
from database import create_connection

class LoginWindow(QWidget):
    # Signal to send the role (admin/seller) back to main.py upon success
    login_success = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tajammal General Store - Login")
        
        # 1. Fixed Window Size (1350 width, 700 height)
        self.setFixedSize(1350, 700)
        
        # 2. Center the window on the screen
        self.center_window()
        
        # 3. Build the UI
        self.init_ui()

    def center_window(self):
        """Moves the window to the center of the primary screen."""
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        # --- Main Layout ---
        main_layout = QHBoxLayout()
        
        # Add 20px margin on all sides to create the "frame" look
        margin_size = 20 
        main_layout.setContentsMargins(margin_size, margin_size, margin_size, margin_size)
        main_layout.setSpacing(0)

        # ===========================
        # --- LEFT SIDE: IMAGE ---
        # ===========================
        self.image_label = QLabel()
        self.image_label.setStyleSheet("background-color: #2c3e50; border-top-left-radius: 8px; border-bottom-left-radius: 8px;")
        
        # Calculate Dimensions
        img_target_width = 600
        # Height = Window(700) - TopMargin(20) - BottomMargin(20) = 660
        img_target_height = 700 - (margin_size * 2)
        
        self.image_label.setFixedWidth(img_target_width)
        self.image_label.setFixedHeight(img_target_height)

        # Image Logic (Scaling & Cropping)
        image_path = "General_Store.png"
        
        if os.path.exists(image_path):
            src_pixmap = QPixmap(image_path)
            
            # Scale to fill both width and height (zooms in if needed)
            scaled_pixmap = src_pixmap.scaled(
                img_target_width, 
                img_target_height,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Crop to fit the box exactly
            final_pixmap = scaled_pixmap.copy(0, 0, img_target_width, img_target_height)

            self.image_label.setPixmap(final_pixmap)
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        else:
            self.image_label.setText("Store Image Not Found")
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.image_label.setStyleSheet("color: white; background-color: #4a69bd;")

        # ===========================
        # --- RIGHT SIDE: FORM ---
        # ===========================
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #ffffff; border-top-right-radius: 8px; border-bottom-right-radius: 8px;")
        
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(60, 60, 60, 60)
        
        # [KEY FIX] Set global spacing to small (8px) so labels stay close to inputs
        right_layout.setSpacing(8) 

        # 1. Welcome Header
        welcome_label = QLabel("Welcome to\nTajammal General Store")
        welcome_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: #2c3e50; border: none;")
        welcome_label.setWordWrap(True)

        sub_label = QLabel("Please login to continue")
        sub_label.setFont(QFont("Segoe UI", 14))
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label.setStyleSheet("color: #7f8c8d; margin-bottom: 30px; border: none;")

        # 2. Styles
        input_style = """
            QLineEdit { 
                border: 2px solid #bdc3c7; 
                border-radius: 8px; 
                padding: 12px; 
                font-size: 16px; 
            }
            QLineEdit:focus { border: 2px solid #27ae60; }
        """
        btn_style = """
            QPushButton { 
                background-color: #27ae60; 
                color: white; 
                font-size: 18px; 
                font-weight: bold; 
                border-radius: 8px; 
                padding: 12px;
            }
            QPushButton:hover { background-color: #2ecc71; }
            QPushButton:pressed { background-color: #219150; }
        """

        # 3. Input Fields
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter your username")
        self.user_input.setFixedHeight(55)
        self.user_input.setStyleSheet(input_style)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Enter your password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setFixedHeight(55)
        self.pass_input.setStyleSheet(input_style)
        # Allow pressing 'Enter' inside password box to trigger login
        self.pass_input.returnPressed.connect(self.check_login)

        # 4. Login Button
        self.btn_login = QPushButton("Login")
        self.btn_login.setFixedHeight(60)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.clicked.connect(self.check_login)
        self.btn_login.setStyleSheet(btn_style)

        # 5. Assemble Layout
        right_layout.addStretch()
        right_layout.addWidget(welcome_label)
        right_layout.addWidget(sub_label)
        
        # Group: Username
        right_layout.addWidget(QLabel("Username"))
        right_layout.addWidget(self.user_input)
        
        # Add manual spacing between inputs
        right_layout.addSpacing(20) 

        # Group: Password
        right_layout.addWidget(QLabel("Password"))
        right_layout.addWidget(self.pass_input)
        
        # Add manual spacing before button
        right_layout.addSpacing(30) 
        
        right_layout.addWidget(self.btn_login)
        right_layout.addStretch()

        right_widget.setLayout(right_layout)

        # Add both sides to main layout
        main_layout.addWidget(self.image_label) 
        main_layout.addWidget(right_widget)

        self.setLayout(main_layout)

    def check_login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not username and not password:
            QMessageBox.warning(self, "Input Error", "Please enter both Username and Password.")
            return

        if not username:
            QMessageBox.warning(self, "Input Error", "Please enter your Username.")
            self.user_input.setFocus()
            return

        if not password:
            QMessageBox.warning(self, "Input Error", "Please enter your Password.")
            self.pass_input.setFocus()
            return

        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role FROM users WHERE username = %s AND password = %s",
                    (username, password)
                )
                result = cursor.fetchone()

                if result:
                    role = result[0]
                    print(f"Login Success: {username} ({role})")
                    self.login_success.emit(username, role)
                else:
                    QMessageBox.warning(
                        self,
                        "Login Failed",
                        "Invalid Username or Password.\nPlease try again."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Database Error", str(e))
            finally:
                conn.close()
