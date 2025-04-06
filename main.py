import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QComboBox,
                             QMessageBox, QTableWidget, QTableWidgetItem)

from PyQt5.QtGui import QPalette, QColor

import csv
import os


class SystemConfig:
    CURRENT_TIME = "2025-04-04 04:10:03"
    CURRENT_USER = "emmaeng700"


class Student:
    def __init__(self, student_id, name, password):
        self.student_id = student_id
        self.name = name
        self.password = password
        self.registered_courses = set()
        self.registration_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.last_login = None

    def add_course(self, course_id):
        self.registered_courses.add(course_id)

    def remove_course(self, course_id):
        if course_id in self.registered_courses:
            self.registered_courses.remove(course_id)

    def get_courses(self):
        return list(self.registered_courses)

    def update_last_login(self):
        self.last_login = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'password': self.password,
            'registered_courses': ','.join(self.registered_courses) if self.registered_courses else '',
            'registration_date': self.registration_date,
            'last_login': self.last_login if self.last_login else ''
        }



class MainWindow(QMainWindow):

    def __init__(self, enrollment_system, student_id, login_callback):  # Make callback required
        super().__init__()
        self.enrollment_system = enrollment_system
        self.current_student_id = student_id
        self.login_callback = login_callback  # Store the callback
        self.set_background_color()  # Add this method
        self.init_ui()

    # def set_background_color(self):
    #     # Create and set a warm yellow background
    #     palette = self.palette()
    #     palette.setColor(QPalette.Window, QColor(255, 253, 208))  # Warm yellow color
    #     self.setPalette(palette)
    #     self.setAutoFillBackground(True)

    def set_background_color(self):
        # Create and set a deeper yellow background
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 223, 0))  # Deeper yellow color
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def init_ui(self):
        self.setWindowTitle('University Course Registration System')
        self.setGeometry(100, 100, 1200, 800)  # Made window larger for better table display

        # Create central widget and layout
        central_widget = QWidget()
        # Create central widget and layout
        central_widget = QWidget()
        central_widget.setStyleSheet("""
                    QWidget {
                        background-color: rgba(255, 223, 0, 0.9);  /* Deeper yellow with transparency */
                    }
                    QTableWidget {
                        background-color: rgba(255, 255, 255, 0.95);
                        border-radius: 5px;
                        border: 1px solid #ddd;
                    }
                    QLabel {
                        color: #2c3e50;
                        background: transparent;
                    }
                    QPushButton {
                        padding: 4px 4px;
                        border-radius: 12px;
                        color: white;
                        min-width: 80px;
                        font-size: 14px;  /* Increased base font size */
                        font-weight: bold;
                    }
                    #successButton {
                        background-color: #2ecc71;  /* Green */
                        font-size: 9px;  /* Bigger font for enroll */
                    }
                    #successButton:hover {
                        background-color: #27ae60;
                    }
                    #dangerButton {
                        background-color: #e74c3c;  /* Red */
                        font-size: 9px;  /* Bigger font for drop */
                    }
                    #dangerButton:hover {
                        background-color: #c0392b;
                    }
                    #enrolledButton {
                        background-color: #95a5a6;  /* Gray */
                        font-size: 15px;
                    }
                    #fullButton {
                        background-color: #bdc3c7;  /* Light gray */
                        font-size: 15px;
                    }
                    #logoutButton {
                        background-color: #e67e22;  /* Orange */
                        min-width: 100px;
                        padding: 8px 15px;
                        font-size: 14px;
                    }
                    #logoutButton:hover {
                        background-color: #d35400;
                    }
                    #timeLabel {
                        font-weight: bold;
                        color: #2c3e50;
                    }
                    #welcomeLabel {
                        font-size: 18px;
                        font-weight: bold;
                        color: #2c3e50;
                        margin: 10px 0;
                    }
                    #sectionHeader {
                        font-size: 16px;
                        font-weight: bold;
                        color: #2c3e50;
                        margin-top: 15px;
                    }
                    QTableWidget::item {
                        padding: 5px;
                    }
                    QHeaderView::section {
                        background-color: #f8f9fa;
                        padding: 5px;
                        border: 1px solid #ddd;
                        font-weight: bold;
                        color: #2c3e50;
                    }
                """)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header with system info
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        time_label = QLabel(f"System Time: {SystemConfig.CURRENT_TIME}")
        time_label.setObjectName("timeLabel")
        # user_label = QLabel(f"Current User: {SystemConfig.CURRENT_USER}")
        student_name = self.enrollment_system.students[self.current_student_id].name
        user_label = QLabel(f"Current User: {student_name}")
        user_label.setObjectName("timeLabel")

        header_layout.addWidget(time_label)
        header_layout.addWidget(user_label)
        header_layout.addStretch()

        layout.addWidget(header_widget)

        # Welcome message
        welcome_label = QLabel(f"Welcome, {self.enrollment_system.students[self.current_student_id].name}!")
        welcome_label.setObjectName("welcomeLabel")
        layout.addWidget(welcome_label)

        # Enrolled Courses Section
        enrolled_header = QLabel("My Enrolled Courses")
        enrolled_header.setObjectName("sectionHeader")
        layout.addWidget(enrolled_header)

        self.enrolled_table = QTableWidget()
        self.enrolled_table.setColumnCount(5)
        self.enrolled_table.setHorizontalHeaderLabels(['Course ID', 'Name', 'Instructor', 'Schedule', 'Action'])
        self.enrolled_table.horizontalHeader().setStretchLastSection(True)
        self.enrolled_table.setMinimumHeight(200)  # Set minimum height for better visibility
        layout.addWidget(self.enrolled_table)

        # Spacer between tables
        spacer = QWidget()
        spacer.setMinimumHeight(20)
        layout.addWidget(spacer)

        # Available Courses Section
        available_header = QLabel("Available Courses")
        available_header.setObjectName("sectionHeader")
        layout.addWidget(available_header)

        self.available_table = QTableWidget()
        self.available_table.setColumnCount(5)
        self.available_table.setHorizontalHeaderLabels(['Course ID', 'Name', 'Instructor', 'Schedule', 'Action'])
        self.available_table.horizontalHeader().setStretchLastSection(True)
        self.available_table.setMinimumHeight(200)  # Set minimum height for better visibility
        layout.addWidget(self.available_table)

        # Spacer before logout button
        spacer = QWidget()
        spacer.setMinimumHeight(20)
        layout.addWidget(spacer)

        # Logout button at bottom
        logout_widget = QWidget()
        logout_layout = QHBoxLayout(logout_widget)
        logout_layout.addStretch()

        # logout_button = QPushButton("Logout")
        # logout_button.clicked.connect(self.logout)
        # logout_layout.addWidget(logout_button)
        logout_button = QPushButton("Logout")
        logout_button.setObjectName("logoutButton")  # Add this line
        logout_button.clicked.connect(self.logout)
        logout_layout.addWidget(logout_button)

        layout.addWidget(logout_widget)

        # Update tables
        self.update_course_tables()

    def update_course_tables(self):
        def format_schedule(schedule_dict):
            """Convert schedule dictionary to readable format"""
            if not schedule_dict:
                return "No schedule set"

            # Convert string representation of dictionary to actual dictionary if needed
            if isinstance(schedule_dict, str):
                try:
                    schedule_dict = eval(schedule_dict)
                except:
                    return "Invalid schedule format"

            # Sort days to ensure consistent order
            days_order = {
                'Monday': 1,
                'Tuesday': 2,
                'Wednesday': 3,
                'Thursday': 4,
                'Friday': 5
            }

            formatted_schedule = []
            for day in sorted(schedule_dict.keys(), key=lambda x: days_order.get(x, 99)):
                start_time, end_time = schedule_dict[day]
                formatted_schedule.append(f"{day[:3]} {start_time}-{end_time}")

            return " | ".join(formatted_schedule)

        # Helper function for already enrolled message
        def show_already_enrolled_message(course_name):
            QMessageBox.information(
                self,
                "Already Taking Course",
                f"You are already taking {course_name}. Check your enrolled courses above."
            )

        # Update enrolled courses
        enrolled_courses = self.enrollment_system.get_student_courses(self.current_student_id)
        self.enrolled_table.setRowCount(len(enrolled_courses))

        for i, course in enumerate(enrolled_courses):
            self.enrolled_table.setItem(i, 0, QTableWidgetItem(course.course_id))
            self.enrolled_table.setItem(i, 1, QTableWidgetItem(course.name))
            self.enrolled_table.setItem(i, 2, QTableWidgetItem(course.instructor))

            # Format schedule nicely
            schedule_text = format_schedule(course.schedule)
            schedule_item = QTableWidgetItem(schedule_text)
            schedule_item.setToolTip(schedule_text)  # Show full text on hover
            self.enrolled_table.setItem(i, 3, schedule_item)

            drop_button = QPushButton("Drop Course")
            drop_button.setObjectName("dangerButton")
            drop_button.clicked.connect(lambda checked, cid=course.course_id: self.drop_course(cid))
            self.enrolled_table.setCellWidget(i, 4, drop_button)

        # Update available courses
        available_courses = self.enrollment_system.get_available_courses(self.current_student_id)
        self.available_table.setRowCount(len(available_courses))

        enrolled_course_ids = {course.course_id for course in enrolled_courses}

        for i, course in enumerate(available_courses):
            self.available_table.setItem(i, 0, QTableWidgetItem(course.course_id))
            self.available_table.setItem(i, 1, QTableWidgetItem(course.name))
            self.available_table.setItem(i, 2, QTableWidgetItem(course.instructor))

            # Format schedule nicely
            schedule_text = format_schedule(course.schedule)
            schedule_item = QTableWidgetItem(schedule_text)
            schedule_item.setToolTip(schedule_text)  # Show full text on hover
            self.available_table.setItem(i, 3, schedule_item)

            enroll_button = QPushButton("Enroll")
            if course.course_id in enrolled_course_ids:
                enroll_button.setText("✓")  # Checkmark instead of "Enrolled"
                enroll_button.setEnabled(True)  # Keep enabled for message
                enroll_button.setObjectName("enrolledButton")
                # Use lambda to pass course name to message function
                enroll_button.clicked.connect(
                    lambda checked, name=course.name: show_already_enrolled_message(name)
                )
            elif course.is_full():
                enroll_button.setText("Full")
                enroll_button.setEnabled(False)
                enroll_button.setObjectName("fullButton")
            else:
                enroll_button.setObjectName("successButton")
                enroll_button.clicked.connect(
                    lambda checked, cid=course.course_id: self.enroll_course(cid)
                )
            self.available_table.setCellWidget(i, 4, enroll_button)

            # Adjust column widths
            for table in [self.enrolled_table, self.available_table]:
                # Set specific widths for each column
                table.setColumnWidth(0, 100)  # Course ID
                table.setColumnWidth(1, 200)  # Name
                table.setColumnWidth(2, 250)  # Instructor - made wider
                table.setColumnWidth(3, 300)  # Schedule - made wider
                table.setColumnWidth(4, 80)  # Action buttons - made narrower


    def drop_course(self, course_id):
        success, message = self.enrollment_system.drop_course(self.current_student_id, course_id)

        if success:
            QMessageBox.information(self, "Success", message)
            self.update_course_tables()
        else:
            QMessageBox.warning(self, "Error", message)

    def enroll_course(self, course_id):
        success, message = self.enrollment_system.enroll_student(self.current_student_id, course_id)

        if success:
            QMessageBox.information(self, "Success", message)
            self.update_course_tables()
        else:
            QMessageBox.warning(self, "Error", message)

    # def logout(self):
    #     self.enrollment_system.logout()
    #     self.close()

    def logout(self):
        """Handle logout and return to login window"""
        self.enrollment_system.logout()
        self.close()
        if self.login_callback:  # Check if callback exists
            self.login_callback()  # Show login window if callback exists


class ResetPasswordWindow(QWidget):
    def __init__(self, enrollment_system, login_callback, pre_filled_id=""):
        super().__init__()
        self.enrollment_system = enrollment_system
        self.login_callback = login_callback
        self.pre_filled_id = pre_filled_id
        self.set_background_color()
        self.init_ui()

    def set_background_color(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(135, 206, 235))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def init_ui(self):
        self.setWindowTitle('Reset Password')
        self.setGeometry(300, 300, 400, 300)

        # Use same style as registration window
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(176, 224, 230, 0.9);
            }
            QLabel {
                color: #1a3c5e;
                background: transparent;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #4682B4;
                border-radius: 4px;
                background: white;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                color: white;
                min-width: 100px;
                background-color: #5F9EA0;
                border: none;
            }
            QPushButton:hover {
                background-color: #4A7F81;
            }
            #successButton {
                background-color: #4682B4;
            }
            #successButton:hover {
                background-color: #357099;
            }
            #timeLabel {
                font-weight: bold;
                color: #1a3c5e;
            }
            #welcomeLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1a3c5e;
                margin: 10px 0;
            }
        """)

        layout = QVBoxLayout()

        # Header
        header_label = QLabel("Reset Password")
        header_label.setObjectName("welcomeLabel")
        layout.addWidget(header_label)

        # Form
        form_layout = QVBoxLayout()

        # Student ID
        form_layout.addWidget(QLabel("Student ID:"))
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("Enter your Student ID")
        if self.pre_filled_id:
            self.student_id_input.setText(self.pre_filled_id)
        form_layout.addWidget(self.student_id_input)

        # Name verification
        form_layout.addWidget(QLabel("Verify Full Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name for verification")
        form_layout.addWidget(self.name_input)

        # New Password
        form_layout.addWidget(QLabel("New Password:"))
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText("Enter new password (minimum 6 characters)")
        form_layout.addWidget(self.new_password_input)

        # Confirm Password
        form_layout.addWidget(QLabel("Confirm Password:"))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        form_layout.addWidget(self.confirm_password_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        reset_button = QPushButton("Reset Password")
        reset_button.setObjectName("successButton")
        reset_button.clicked.connect(self.reset_password)

        back_button = QPushButton("Back to Login")
        back_button.clicked.connect(self.back_to_login)

        button_layout.addWidget(reset_button)
        button_layout.addWidget(back_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def reset_password(self):
        student_id = self.student_id_input.text().strip()
        name = self.name_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        # Validation
        if not all([student_id, name, new_password, confirm_password]):
            QMessageBox.warning(self, "Error", "All fields are required!")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match!")
            return

        if len(new_password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters long!")
            return

        # Check if student exists and verify name
        if student_id not in self.enrollment_system.students:
            QMessageBox.warning(self, "Error", "Student ID not found!")
            return

        student = self.enrollment_system.students[student_id]
        if student.name.lower() != name.lower():
            QMessageBox.warning(self, "Error", "Name verification failed!")
            return

        # Update password
        student.password = new_password
        self.enrollment_system.save_data()

        QMessageBox.information(self, "Success", "Password has been reset successfully!")
        self.back_to_login()

    def back_to_login(self):
        self.close()
        self.login_callback()


class LoginWindow(QMainWindow):
    def __init__(self, enrollment_system):
        super().__init__()
        self.enrollment_system = enrollment_system
        self.set_background_color()  # Add this line
        self.init_ui()

    def set_background_color(self):
        # Create and set a deeper sea blue background
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(135, 206, 235))  # Sky blue / Sea blue
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def init_ui(self):
        self.setWindowTitle('Student Login')
        self.setGeometry(300, 300, 400, 300)

        # Create single central widget
        central_widget = QWidget()
        central_widget.setStyleSheet("""
                    QWidget {
                        background-color: rgba(176, 224, 230, 0.9);  /* Powder blue with transparency */
                    }
                    QLabel {
                        color: #1a3c5e;  /* Darker blue for better contrast */
                        background: transparent;
                    }
                    QLineEdit {
                        padding: 8px;
                        border: 1px solid #4682B4;  /* Steel blue border */
                        border-radius: 4px;
                        background: white;
                    }
                    QPushButton {
                        padding: 8px 15px;
                        border-radius: 4px;
                        color: white;
                        min-width: 100px;
                        background-color: #5F9EA0;  /* Default button color */
                    }
                    QPushButton:hover {
                        background-color: #4A7F81;  /* Darker shade for hover */
                    }
                    #successButton {
                        background-color: #4682B4;  /* Steel blue */
                        border: none;
                    }
                    #successButton:hover {
                        background-color: #357099;  /* Darker steel blue */
                    }
                    #secondaryButton {
                        background-color: #5F9EA0;  /* Cadet blue */
                        border: none;
                    }
                    #secondaryButton:hover {
                        background-color: #4A7F81;  /* Darker cadet blue */
                    }
                    #timeLabel {
                        font-weight: bold;
                        color: #1a3c5e;  /* Darker blue */
                    }
                    #welcomeLabel {
                        font-size: 18px;
                        font-weight: bold;
                        color: #1a3c5e;  /* Darker blue */
                        margin: 10px 0;
                    }
                    #validationLabel {
                        margin-top: 5px;
                        font-size: 12px;
                    }
                """)
        # Main layout
        layout = QVBoxLayout(central_widget)

        # Header with system time
        time_label = QLabel(f"System Time: {SystemConfig.CURRENT_TIME}")
        time_label.setObjectName("timeLabel")
        layout.addWidget(time_label)

        # Welcome message
        welcome_label = QLabel("Welcome to Course Registration System")
        welcome_label.setObjectName("welcomeLabel")
        layout.addWidget(welcome_label)

        # Form layout
        form_layout = QVBoxLayout()

        form_layout.addWidget(QLabel("Student ID:"))
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("Enter Student ID")
        self.student_id_input.textChanged.connect(self.check_student_id)
        form_layout.addWidget(self.student_id_input)

        # ID status indicator
        self.id_status_label = QLabel("")
        self.id_status_label.setObjectName("validationLabel")
        form_layout.addWidget(self.id_status_label)

        # Password
        form_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter Password")
        form_layout.addWidget(self.password_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("successButton")
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("New User? Register")
        self.register_button.setObjectName("secondaryButton")
        self.register_button.clicked.connect(self.show_registration)

        ####new
        self.forgot_password_button = QPushButton("Forgot Password?")  # Add this button
        self.forgot_password_button.setObjectName("secondaryButton")
        self.forgot_password_button.clicked.connect(self.show_reset_password)


        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        layout.addLayout(button_layout)


        ####new
        # Add forgot password button in a separate layout for better spacing
        forgot_layout = QHBoxLayout()
        forgot_layout.addWidget(self.forgot_password_button)
        layout.addLayout(forgot_layout)

        # Set the central widget
        self.setCentralWidget(central_widget)

    def show_reset_password(self):
        student_id = self.student_id_input.text().strip()
        self.hide()
        self.reset_password_window = ResetPasswordWindow(self.enrollment_system, self.show, student_id)
        self.reset_password_window.show()

    def check_student_id(self):
        """Check if student ID exists while typing"""
        student_id = self.student_id_input.text().strip()

        if not student_id:
            self.id_status_label.setText("")
            return

        if student_id in self.enrollment_system.students:
            self.id_status_label.setText("User exists! Please login.")
            self.id_status_label.setStyleSheet("color: #198754;")  # Green color
            self.register_button.setEnabled(False)
            self.register_button.setToolTip("This user already exists. Please login.")
        else:
            self.id_status_label.setText("New user? Please register.")
            self.id_status_label.setStyleSheet("color: #0d6efd;")  # Blue color
            self.register_button.setEnabled(True)
            self.register_button.setToolTip("Click to register as a new user")

    def login(self):
        student_id = self.student_id_input.text().strip()
        password = self.password_input.text().strip()

        if not all([student_id, password]):
            QMessageBox.warning(self, "Error", "Please enter both Student ID and Password!")
            return

        if student_id not in self.enrollment_system.students:
            QMessageBox.warning(self, "Error",
                                "User does not exist! Please register first.")
            self.register_button.setEnabled(True)
            return

        if self.enrollment_system.authenticate_student(student_id, password):
            self.hide()  # Hide login window instead of closing it
            self.main_window = MainWindow(
                self.enrollment_system,
                student_id,
                lambda: self.show_login()  # Pass the callback as a lambda
            )
            self.main_window.show()
        else:
            QMessageBox.warning(self, "Error", "Invalid Password!")

    def show_login(self):
        """Method to show login window and reset fields"""
        self.student_id_input.clear()
        self.password_input.clear()
        self.id_status_label.setText("")
        self.register_button.setEnabled(True)
        self.show()

    def show_registration(self):
        student_id = self.student_id_input.text().strip()

        if student_id and student_id in self.enrollment_system.students:
            QMessageBox.warning(self, "Error",
                                f"User '{student_id}' already exists! Please login or use a different ID.")
            return

        self.hide()
        self.registration_window = RegistrationWindow(self.enrollment_system, self.show)
        self.registration_window.show()





class RegistrationWindow(QWidget):
    def __init__(self, enrollment_system, login_callback):
        super().__init__()
        self.enrollment_system = enrollment_system
        self.login_callback = login_callback
        self.set_background_color()  # Add this method
        self.init_ui()

    def set_background_color(self):
        # Create and set a deeper sea blue background
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(135, 206, 235))  # Sky blue / Sea blue
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def init_ui(self):
        self.setWindowTitle('Student Registration')
        self.setGeometry(300, 300, 400, 250)

        # Add stylesheet for consistent look
        self.setStyleSheet("""
                    QWidget {
                        background-color: rgba(176, 224, 230, 0.9);  /* Powder blue with transparency */
                    }
                    QLabel {
                        color: #1a3c5e;  /* Darker blue for better contrast */
                        background: transparent;
                    }
                    QLineEdit {
                        padding: 8px;
                        border: 1px solid #4682B4;  /* Steel blue border */
                        border-radius: 4px;
                        background: white;
                    }
                    QPushButton {
                        padding: 8px 15px;
                        border-radius: 4px;
                        color: white;
                        min-width: 100px;
                        background-color: #5F9EA0;  /* Cadet blue */
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #4A7F81;  /* Darker cadet blue */
                    }
                    #successButton {
                        background-color: #4682B4;  /* Steel blue */
                        border: none;
                    }
                    #successButton:hover {
                        background-color: #357099;  /* Darker steel blue */
                    }
                    #timeLabel {
                        font-weight: bold;
                        color: #1a3c5e;  /* Darker blue */
                    }
                    #welcomeLabel {
                        font-size: 18px;
                        font-weight: bold;
                        color: #1a3c5e;  /* Darker blue */
                        margin: 10px 0;
                    }
                    #validationLabel {
                        margin-top: 5px;
                        font-size: 12px;
                    }
                """)

        layout = QVBoxLayout()

        # Header with system time
        time_label = QLabel(f"System Time: {SystemConfig.CURRENT_TIME}")
        time_label.setObjectName("timeLabel")
        layout.addWidget(time_label)

        # Header
        header_label = QLabel("Student Registration")
        header_label.setObjectName("welcomeLabel")
        layout.addWidget(header_label)

        # Form fields
        form_layout = QVBoxLayout()

        # Student ID
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("Student ID (e.g., john123)")
        self.student_id_input.textChanged.connect(self.check_student_id)
        form_layout.addWidget(QLabel("Student ID:"))
        form_layout.addWidget(self.student_id_input)

        # Student ID availability indicator
        self.id_status_label = QLabel("")
        self.id_status_label.setObjectName("validationLabel")
        form_layout.addWidget(self.id_status_label)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter Password (minimum 6 characters)")
        form_layout.addWidget(QLabel("Password:"))
        form_layout.addWidget(self.password_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)
        self.register_button.setObjectName("successButton")

        back_button = QPushButton("Back to Login")
        back_button.clicked.connect(self.back_to_login)

        button_layout.addWidget(self.register_button)
        button_layout.addWidget(back_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def check_student_id(self):
        """Check if student ID is available while typing"""
        student_id = self.student_id_input.text().strip()

        if not student_id:
            self.id_status_label.setText("")
            self.register_button.setEnabled(False)
            return

        if student_id in self.enrollment_system.students:
            self.id_status_label.setText("Student ID already taken!")
            self.id_status_label.setStyleSheet("color: #dc3545;")  # Red color
            self.register_button.setEnabled(False)
        else:
            if student_id.isalnum() and len(student_id) >= 3:
                self.id_status_label.setText("Student ID available!")
                self.id_status_label.setStyleSheet("color: #198754;")  # Green color
                self.register_button.setEnabled(True)
            else:
                self.id_status_label.setText("Student ID must be at least 3 alphanumeric characters")
                self.id_status_label.setStyleSheet("color: #dc3545;")  # Red color
                self.register_button.setEnabled(False)

    def register(self):
        student_id = self.student_id_input.text().strip()
        name = self.name_input.text().strip()
        password = self.password_input.text().strip()

        # Additional validation
        if not all([student_id, name, password]):
            QMessageBox.warning(self, "Error", "All fields are required!")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters long!")
            return

        if not student_id.isalnum():
            QMessageBox.warning(self, "Error", "Student ID must contain only letters and numbers!")
            return

        # Check again if student ID exists (double check)
        if student_id in self.enrollment_system.students:
            QMessageBox.warning(self, "Error", "This Student ID is already registered!")
            return

        # Try to register
        success = self.enrollment_system.add_student(student_id, name, password)

        if success:
            QMessageBox.information(self, "Success", "Registration successful! You can now login.")
            self.back_to_login()
        else:
            QMessageBox.warning(self, "Error", "Registration failed! Please try again.")

    def back_to_login(self):
        self.close()
        self.login_callback()


from datetime import datetime

class Course:
    def __init__(self, course_id, name, instructor, max_students=30, schedule=None, description=None):
        self.course_id = course_id
        self.name = name
        self.instructor = instructor
        self.enrolled_students = set()
        self.max_students = max_students
        self.creation_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.schedule = schedule or {}
        self.description = description or ""

    def add_student(self, student_id):
        if len(self.enrolled_students) < self.max_students:
            self.enrolled_students.add(student_id)
            return True
        return False

    def remove_student(self, student_id):
        if student_id in self.enrolled_students:
            self.enrolled_students.remove(student_id)
            return True
        return False

    def is_full(self):
        return len(self.enrolled_students) >= self.max_students

    def get_enrolled_students(self):
        return list(self.enrolled_students)

    def get_available_slots(self):
        return self.max_students - len(self.enrolled_students)

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'name': self.name,
            'instructor': self.instructor,
            'enrolled_students': ','.join(self.enrolled_students) if self.enrolled_students else '',
            'max_students': str(self.max_students),
            'creation_date': self.creation_date,
            'schedule': str(self.schedule),
            'description': self.description
        }



class EnrollmentSystem:
    def __init__(self):
        self.students = {}
        self.courses = {}
        self.current_user = None
        self.load_data()

    def load_data(self):
        self._ensure_files_exist()
        self.load_students()
        self.load_courses()

    def _ensure_files_exist(self):
        files_and_headers = {
            'students.csv': ['student_id', 'name', 'password', 'registered_courses',
                             'registration_date', 'last_login'],
            'courses.csv': ['course_id', 'name', 'instructor', 'enrolled_students',
                            'max_students', 'creation_date', 'schedule', 'description']
        }

        for filename, headers in files_and_headers.items():
            if not os.path.exists(filename):
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)

    def load_students(self):
        try:
            with open('students.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    student = Student(row['student_id'], row['name'], row['password'])
                    if row['registered_courses']:
                        student.registered_courses = set(row['registered_courses'].split(','))
                    student.registration_date = row['registration_date']
                    student.last_login = row['last_login'] if row['last_login'] else None
                    self.students[row['student_id']] = student
        except FileNotFoundError:
            pass

    def reset_password(self, student_id, new_password):
        if student_id in self.students:
            self.students[student_id].password = new_password
            self.save_data()
            return True
        return False

    def load_courses(self):
        try:
            with open('courses.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    course = Course(
                        row['course_id'],
                        row['name'],
                        row['instructor'],
                        int(row['max_students']),
                        eval(row['schedule']) if row['schedule'] else {},
                        row['description']
                    )
                    if row['enrolled_students']:
                        course.enrolled_students = set(row['enrolled_students'].split(','))
                    course.creation_date = row['creation_date']
                    self.courses[row['course_id']] = course
        except FileNotFoundError:
            pass

    def save_data(self):
        self.save_students()
        self.save_courses()

    def save_students(self):
        with open('students.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'student_id', 'name', 'password', 'registered_courses',
                'registration_date', 'last_login'
            ])
            writer.writeheader()
            for student in self.students.values():
                writer.writerow(student.to_dict())

    def save_courses(self):
        with open('courses.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'course_id', 'name', 'instructor', 'enrolled_students',
                'max_students', 'creation_date', 'schedule', 'description'
            ])
            writer.writeheader()
            for course in self.courses.values():
                writer.writerow(course.to_dict())

    def authenticate_student(self, student_id, password):
        if student_id in self.students:
            student = self.students[student_id]
            if student.password == password:
                student.update_last_login()
                self.current_user = student
                self.save_data()
                return True
        return False

    def add_student(self, student_id, name, password):
        if student_id not in self.students:
            self.students[student_id] = Student(student_id, name, password)
            self.save_data()
            return True
        return False

    def add_course(self, course_id, name, instructor, max_students=30, schedule=None, description=None):
        if course_id not in self.courses:
            self.courses[course_id] = Course(course_id, name, instructor, max_students, schedule, description)
            self.save_data()
            return True
        return False



    def enroll_student(self, student_id, course_id):
        if student_id not in self.students or course_id not in self.courses:
            return False, "Invalid student or course"

        student = self.students[student_id]
        course = self.courses[course_id]

        # Check if already enrolled
        if course_id in student.registered_courses:
            return False, "Already enrolled in this course"

        # Check if course is full
        if course.is_full():
            return False, "Course is full"

        # Check for schedule conflicts
        if self._check_schedule_conflict(student, course):
            return False, "Schedule conflict detected"

        # Proceed with enrollment
        if course.add_student(student_id):
            student.add_course(course_id)
            self.save_data()
            return True, "Enrollment successful"

        return False, "Enrollment failed"

    def _check_schedule_conflict(self, student, new_course):
        if not new_course.schedule:
            return False

        for enrolled_course_id in student.registered_courses:
            enrolled_course = self.courses[enrolled_course_id]
            if enrolled_course.schedule:
                for day, new_times in new_course.schedule.items():
                    if day in enrolled_course.schedule:
                        new_start, new_end = new_times
                        old_start, old_end = enrolled_course.schedule[day]
                        if (new_start < old_end and new_end > old_start):
                            return True
        return False

    def drop_course(self, student_id, course_id):
        if student_id not in self.students:
            return False, "Student not found"

        if course_id not in self.courses:
            return False, "Course not found"

        student = self.students[student_id]
        course = self.courses[course_id]

        # Debug print statements
        print(f"Before drop - Student courses: {student.registered_courses}")
        print(f"Before drop - Course enrollment: {course.enrolled_students}")

        # Check if student is actually enrolled
        if course_id not in student.registered_courses:
            return False, "Student is not enrolled in this course"

        if student_id not in course.enrolled_students:
            return False, "Student not found in course roster"

        # Perform the drop
        student.remove_course(course_id)
        course.remove_student(student_id)

        # Debug print statements
        print(f"After drop - Student courses: {student.registered_courses}")
        print(f"After drop - Course enrollment: {course.enrolled_students}")

        # Save changes immediately
        self.save_data()

        return True, "Course dropped successfully"

    def get_student_courses(self, student_id):
        if student_id in self.students:
            return [self.courses[cid] for cid in self.students[student_id].registered_courses]
        return []


    def get_available_courses(self, student_id):
        student = self.students.get(student_id)
        if not student:
            return []

        # Return all courses instead of filtering out enrolled ones
        return list(self.courses.values())

    def get_course_students(self, course_id):
        if course_id in self.courses:
            return [self.students[sid] for sid in self.courses[course_id].enrolled_students]
        return []

    def logout(self):
        self.current_user = None

    #############################
    # Add these methods to the EnrollmentSystem class

    def validate_student_id(self, student_id):
        return bool(student_id and student_id.isalnum() and len(student_id) >= 3)

    def validate_course_id(self, course_id):
        return bool(course_id and len(course_id) >= 2)

    def add_student(self, student_id, name, password):
        # Input validation
        if not self.validate_student_id(student_id):
            return False

        if not name or len(name.strip()) < 2:
            return False

        if not password or len(password) < 6:
            return False

        if student_id in self.students:
            return False

        self.students[student_id] = Student(student_id, name, password)
        self.save_data()
        return True

    def enroll_student(self, student_id, course_id):
        # Input validation
        if not self.validate_student_id(student_id) or not self.validate_course_id(course_id):
            return False, "Invalid student or course ID"

        if student_id not in self.students or course_id not in self.courses:
            return False, "Student or course not found"

        student = self.students[student_id]
        course = self.courses[course_id]

        # Check if already enrolled
        if course_id in student.registered_courses:
            return False, "Already enrolled in this course"

        # Check course capacity
        if course.is_full():
            return False, "Course has reached maximum capacity"

        # Check schedule conflicts
        if self._check_schedule_conflict(student, course):
            return False, "Schedule conflict detected"

        # Proceed with enrollment
        if course.add_student(student_id):
            student.add_course(course_id)
            self.save_data()
            return True, "Enrollment successful"

        return False, "Enrollment failed"




def main():
    app = QApplication(sys.argv)
    enrollment_system = EnrollmentSystem()
    login_window = LoginWindow(enrollment_system)
    login_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()