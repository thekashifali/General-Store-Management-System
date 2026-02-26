import random
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QDateEdit, QSizePolicy, QMessageBox, QCalendarWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

# --- DATABASE IMPORT ---
# CORRECTED: Importing the function create_connection directly
from database import create_connection

# --- MATPLOTLIB IMPORTS ---
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class AnalyticsManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # --- 1. Header & Filters Container ---
        top_bar = QHBoxLayout()
        
        header = QLabel("Store Analytics & Reports")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50;")
        
        # Filter Layout
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        # --- QDateEdit STYLESHEET ---
        date_style = """
            QDateEdit {
                background-color: white;
                border: 1px solid #ced6e0;
                border-radius: 6px;
                padding: 5px 10px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #2c3e50;
                min-width: 120px;
            }
            
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #ced6e0; 
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            
            /* Arrow Icon (Using border-based triangle as a standard icon replacement) */
            QDateEdit::down-arrow {
                background-color: transparent;
                border-style: solid;
                border-width: 5px;
                border-top-color: #2c3e50; 
                border-right-color: transparent;
                border-left-color: transparent;
                border-bottom-color: transparent;
                width: 0;
                height: 0;
                margin-top: 5px;
            }
            
            QDateEdit:focus {
                border: 1px solid #3498db; 
            }
        """

        # --- QCalendarWidget STYLESHEET (FIXES TEXT COLOR) ---
        calendar_style = """
            QCalendarWidget QWidget {
                color: #2c3e50; /* Ensure all general text is dark */
                background-color: white; 
                alternate-background-color: #f5f6fa;
            }
            
            QCalendarWidget QToolButton {
                color: #2c3e50; /* Navigation arrows and Month/Year text */
                font-weight: bold;
                background-color: #ecf0f1;
            }
            
            QCalendarWidget QAbstractItemView:enabled {
                color: #2c3e50; /* Day numbers */
                selection-background-color: #3498db; 
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #bdc3c7;
            }
        """
        
        # From Date
        lbl_from = QLabel("From:")
        lbl_from.setFont(QFont("Segoe UI", 11))
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        # FIX: Apply calendar style here to the actual calendar object
        self.date_from.calendarWidget().setStyleSheet(calendar_style)
        self.date_from.setDisplayFormat("dd MMM yyyy") 
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.setStyleSheet(date_style)

        # To Date
        lbl_to = QLabel("To:")
        lbl_to.setFont(QFont("Segoe UI", 11))
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        # FIX: Apply calendar style here to the actual calendar object
        self.date_to.calendarWidget().setStyleSheet(calendar_style)
        self.date_to.setDisplayFormat("dd MMM yyyy")
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setStyleSheet(date_style)

        # Apply Button (REDUCED SIZE)
        btn_apply = QPushButton("Apply Filter")
        btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50; 
                color: white; 
                padding: 6px 15px; 
                border-radius: 6px; 
                font-weight: 600;
                font-family: 'Segoe UI';
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        btn_apply.clicked.connect(self.refresh_charts)
        
        # Add widgets to layout
        filter_layout.addWidget(lbl_from)
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(lbl_to)
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(btn_apply)
        
        # Assemble Top Bar
        top_bar.addWidget(header)
        top_bar.addStretch()
        top_bar.addLayout(filter_layout)

        layout.addLayout(top_bar)
        
        # --- 2. Matplotlib Canvas ---
        if not MATPLOTLIB_AVAILABLE:
            error_lbl = QLabel("Matplotlib is missing. Please run: pip install matplotlib")
            error_lbl.setStyleSheet("color: red; font-size: 16px; margin-top: 20px;")
            layout.addWidget(error_lbl)
            layout.addStretch()
            self.setLayout(layout)
            return

        # Create Figure
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.figure.set_tight_layout(True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Initial chart refresh
        self.refresh_charts()

    def refresh_charts(self):
        """Fetches data and redraws the 4 charts."""
        if not MATPLOTLIB_AVAILABLE: return

        self.figure.clear()
        
        # Add 4 subplots
        ax1 = self.figure.add_subplot(221) 
        ax2 = self.figure.add_subplot(222) 
        ax3 = self.figure.add_subplot(223) 
        ax4 = self.figure.add_subplot(224) 

        # --- A. FETCH REAL DATA ---
        categories = {} 
        top_items_names = []
        top_items_stock = []
        
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Data for Category Pie Chart
                cursor.execute("SELECT category, SUM(buying_price * stock) FROM products GROUP BY category")
                for r in cursor.fetchall():
                    categories[r[0]] = float(r[1]) if r[1] else 0
                
                # Data for Top Items Bar Chart
                cursor.execute("SELECT name, stock FROM products ORDER BY stock DESC LIMIT 5")
                for r in cursor.fetchall():
                    top_items_names.append(r[0])
                    top_items_stock.append(r[1])
            except Exception as e:
                print("Analytics DB Error:", e)
            finally:
                conn.close()

        # --- B. GENERATE DUMMY DATA (For Sales/Profit Trends) ---
        days = []
        sales_data = []
        profit_data = []
        
        start_date = self.date_from.date().toPyDate()
        end_date = self.date_to.date().toPyDate()
        current = start_date
        
        # Loop to create daily points
        while current <= end_date:
            days.append(current.strftime("%d-%b"))
            sales_data.append(random.randint(5000, 25000))
            profit_data.append(random.randint(1000, 6000))
            current += datetime.timedelta(days=1)
            if len(days) > 12: break 

        # --- C. DRAW CHARTS ---
        
        # 1. Sales Trend
        ax1.plot(days, sales_data, marker='o', color='#2980b9', linewidth=2)
        ax1.set_title("Sales Trend (Selected Range)", fontsize=10, fontweight='bold')
        ax1.grid(True, linestyle='--', alpha=0.5)
        ax1.tick_params(axis='x', rotation=30, labelsize=8)

        # 2. Profit Trend
        ax2.fill_between(days, profit_data, color='#27ae60', alpha=0.4)
        ax2.plot(days, profit_data, color='#27ae60', marker='x')
        ax2.set_title("Net Profit Analysis", fontsize=10, fontweight='bold')
        ax2.grid(True, linestyle='--', alpha=0.5)
        ax2.tick_params(axis='x', rotation=30, labelsize=8)

        # 3. Top Items (Real Data)
        if top_items_names:
            bars = ax3.bar(top_items_names, top_items_stock, color=['#e74c3c', '#e67e22', '#f1c40f', '#3498db', '#9b59b6'])
            ax3.set_title("Top Stock Items", fontsize=10, fontweight='bold')
            ax3.tick_params(axis='x', rotation=15, labelsize=8)
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontsize=8)
        else:
            ax3.text(0.5, 0.5, "No Data", ha='center')

        # 4. Categories (Real Data)
        if categories:
            ax4.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', 
                    startangle=90, textprops={'fontsize': 8}, 
                    colors=['#1abc9c', '#3498db', '#9b59b6', '#34495e', '#f1c40f'])
            ax4.set_title("Stock Value by Category", fontsize=10, fontweight='bold')
        else:
            ax4.text(0.5, 0.5, "No Data", ha='center')

        self.canvas.draw()