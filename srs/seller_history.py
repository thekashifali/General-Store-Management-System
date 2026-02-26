from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDateEdit, QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
from database import create_connection

class SellerHistory(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def showEvent(self, event):
        """Refreshes data and resets dates to Today when tab opens."""
        today = QDate.currentDate()
        self.date_from.setDate(today)
        self.date_to.setDate(today)
        self.load_history()
        super().showEvent(event)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 1. HEADER
        header_label = QLabel("Sales History")
        header_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50;")

        # 2. FILTER SECTION
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dcdde1;
                border-radius: 8px;
            }
            QLabel {
                font-weight: bold;
                color: #555;
                border: none;
            }
            QDateEdit {
                padding: 5px; 
                border: 1px solid #bdc3c7; 
                border-radius: 4px;
            }
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                color: black;
            }
            /* Calendar Widget Styling */
            QCalendarWidget QWidget {
                alternate-background-color: #f8f9fa; 
                color: black;
            }
            QCalendarWidget QToolButton {
                color: black;
                font-weight: bold;
                icon-size: 20px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: black;
                background-color: white;
                selection-background-color: #2980b9;
                selection-color: white;
            }
        """)
        
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 10, 15, 10)
        filter_layout.setSpacing(15)

        # -- From Date --
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.setDate(QDate.currentDate())
        self.date_from.setFixedWidth(120)
        self.date_from.dateChanged.connect(self.update_date_constraints)

        # -- To Date --
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setFixedWidth(120)

        # -- Search Bar --
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Sale ID...")
        self.search_input.textChanged.connect(self.filter_table_rows)

        # -- Apply Button --
        btn_refresh = QPushButton("Apply Filter")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                padding: 6px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        btn_refresh.clicked.connect(self.load_history)

        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(QLabel("|"))
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(btn_refresh)

        # =========================================================
        # ✅ NEW: SUMMARY CARDS (KARTS)
        # =========================================================
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # Create the 3 Cards
        self.card_sales = self.create_card("Total Sales", "0", "#3498db") # Blue
        self.card_paid = self.create_card("Total Paid", "Rs 0.00", "#27ae60") # Green
        self.card_loan = self.create_card("Total Loan", "Rs 0.00", "#c0392b") # Red

        cards_layout.addWidget(self.card_sales)
        cards_layout.addWidget(self.card_paid)
        cards_layout.addWidget(self.card_loan)

        # 3. TABLE SETUP
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Sale ID", "Date", "Payment Type",
            "Total Amount", "Paid", "Remaining"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setStyleSheet(self.table_style())

        # ADD TO MAIN LAYOUT
        layout.addWidget(header_label)
        layout.addWidget(filter_frame)
        layout.addLayout(cards_layout) # Add Cards Here
        layout.addWidget(self.table)

        self.update_date_constraints()

    # =========================
    # HELPER: CREATE CARD
    # =========================
   # =========================
    # HELPER: CREATE CARD (UPDATED)
    # =========================
    def create_card(self, title, value, color_hex):
        frame = QFrame()
        
        # CHANGED: Background is now the color, Text will be white
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_hex};
                border-radius: 10px;
                border: 1px solid {color_hex};
            }}
        """)
        
        # Add shadow for "pop" effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50)) # Slightly darker shadow
        shadow.setOffset(0, 4)
        frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15) # Add some padding inside
        
        # Title Text -> White with slight transparency for style
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        lbl_title.setStyleSheet("color: #f0f0f0; border: none; background: transparent;") 
        
        # Value Text -> Pure White and Bold
        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        lbl_value.setStyleSheet("color: white; border: none; background: transparent;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        # Store for updates
        frame.value_label = lbl_value 
        return frame

    # =========================
    # DATE CONSTRAINT LOGIC
    # =========================
    def update_date_constraints(self):
        new_min_date = self.date_from.date()
        self.date_to.setMinimumDate(new_min_date)
        if self.date_to.date() < new_min_date:
            self.date_to.setDate(new_min_date)

    # =========================
    # STYLES & LOGIC
    # =========================
    def table_style(self):
        return """
        QTableWidget {
            background-color: white;
            alternate-background-color: #f8f9fa;
            border: 1px solid #dcdde1;
            font-size: 14px;
            gridline-color: #ecf0f1;
            selection-background-color: #2980b9; 
            selection-color: white;
        }
        QHeaderView::section {
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            font-weight: bold;
            border: none;
        }
        
        QScrollBar:vertical {
            border: none;
            background: #ecf0f1;
            width: 12px;
            margin: 0px; 
        }
        QScrollBar::handle:vertical {
            background-color: #2c3e50;
            min-height: 20px;
            border-radius: 6px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
            border: none;
        }
        """

    def filter_table_rows(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0) 
            if search_text in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    # =========================
    # LOAD SALES HISTORY & CALCULATE TOTALS
    # =========================
    def load_history(self):
        conn = create_connection()
        if conn is None:
            return
        
        date_from_str = self.date_from.date().toString("yyyy-MM-dd") + " 00:00:00"
        date_to_str = self.date_to.date().toString("yyyy-MM-dd") + " 23:59:59"

        try:
            cursor = conn.cursor()

            # FIX: Using %s because you are using MySQL
            query = """
                SELECT sale_id, sale_date, payment_type,
                       total_amount, paid_amount
                FROM sales
                WHERE sale_date BETWEEN %s AND %s
                ORDER BY sale_date DESC
            """
            
            cursor.execute(query, (date_from_str, date_to_str))
            
            rows = cursor.fetchall()
            
            self.table.setRowCount(0)
            
            # --- Initialize Counters for Cards ---
            count_sales = 0
            sum_paid = 0.0
            sum_loan = 0.0

            for r, row in enumerate(rows):
                sale_id, date, pay_type, total, paid = row
                remaining = float(total) - float(paid)

                # Update Sums
                count_sales += 1
                sum_paid += float(paid)
                sum_loan += remaining

                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(str(sale_id)))
                self.table.setItem(r, 1, QTableWidgetItem(str(date)))
                self.table.setItem(r, 2, QTableWidgetItem(pay_type.capitalize()))
                self.table.setItem(r, 3, QTableWidgetItem(f"{float(total):.2f}"))
                self.table.setItem(r, 4, QTableWidgetItem(f"{float(paid):.2f}"))
                
                # Color logic for remaining balance
                rem_item = QTableWidgetItem(f"{remaining:.2f}")
                if remaining > 0:
                     rem_item.setForeground(QColor("#c0392b")) # Red
                     rem_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                else:
                     rem_item.setForeground(QColor("#27ae60")) # Green
                
                self.table.setItem(r, 5, rem_item)
                
                for col in range(6):
                    self.table.item(r, col).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # --- Update Cards UI ---
            self.card_sales.value_label.setText(str(count_sales))
            self.card_paid.value_label.setText(f"Rs {sum_paid:,.2f}")
            self.card_loan.value_label.setText(f"Rs {sum_loan:,.2f}")

        except Exception as e:
            print(f"Error loading history: {e}")
        finally:
            conn.close()