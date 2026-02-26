import sys
from PyQt6.QtWidgets import QApplication

from login import LoginWindow
from admin import AdminDashboard
from seller import SellerDashboard


class StoreManagerApp:
    def __init__(self):
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.handle_login)
        self.login_window.show()

        self.dashboard = None  # admin or seller

    def handle_login(self, username, role):
        print(f"Login Success: {username} ({role})")

        # hide login instead of closing
        self.login_window.hide()

        # close old dashboard if exists
        if self.dashboard:
            self.dashboard.close()
            self.dashboard = None

        # open dashboard by role
        if role == "admin":
            self.dashboard = AdminDashboard()
        elif role == "seller":
            self.dashboard = SellerDashboard(username)
        else:
            print("Unknown role")
            self.login_window.show()
            return

        # connect logout signal
        self.dashboard.logout_requested.connect(self.show_login)

        self.dashboard.show()

    def show_login(self):
        # close dashboard
        if self.dashboard:
            self.dashboard.close()
            self.dashboard = None

        # show login again
        self.login_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = StoreManagerApp()
    sys.exit(app.exec())
