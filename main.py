from PyQt6.QtWidgets import QApplication, QGridLayout, QWidget, QLabel, QPushButton, QLineEdit, QComboBox, \
    QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sys
import mysql.connector


class Database:
    def __init__(self, host="localhost", user="root", password="Dhruva@1", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Add Menu item to File Menu
        add_action = QAction(QIcon("icons/add.png"), "Add", self)
        add_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_action)

        # Add Menu item to Help Menu
        help_action = QAction("About", self)
        help_menu_item.addAction(help_action)
        help_action.triggered.connect(self.about)

        # Add Menu item to File Menu
        edit_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_action.triggered.connect(self.search_widget)
        edit_menu_item.addAction(edit_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Add Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_action)
        toolbar.addAction(edit_action)

        # Add Status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def load_table(self):
        connection = Database().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
        connection.close()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search_widget(self):
        search_dialog = SearchDialog()
        search_dialog.exec()

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        content = """
        This app helps us to manage student records
        """
        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        # Get the student name from table
        index = main_win.table.currentRow()
        student_name = main_win.table.item(index, 1).text()

        # Get Student ID
        self.stud_id = main_win.table.item(index, 0).text()

        self.name = QLineEdit(student_name)
        self.name.setPlaceholderText("Enter Name...")
        layout.addWidget(self.name)

        # Get the student name from table
        course = main_win.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Maths", "Physics", "Chemistry"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course)
        layout.addWidget(self.course_name)

        # Get the student name from table
        mobile_num = main_win.table.item(index, 3).text()
        self.mobile_nr = QLineEdit(mobile_num)
        self.mobile_nr.setPlaceholderText("Enter Mobile Number...")
        layout.addWidget(self.mobile_nr)

        submit = QPushButton("Submit")
        submit.clicked.connect(self.update_student)
        layout.addWidget(submit)

        self.setLayout(layout)

    def update_student(self):
        name = self.name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile_nr.text()
        student_id = self.stud_id
        connection = Database().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile_nr = %s WHERE id = %s",
                       (name, course, mobile, student_id))
        connection.commit()
        cursor.close()
        connection.close()
        # To refresh the table
        main_win.load_table()
        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to Delete")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)

        yes.clicked.connect(self.delete_record)

    def delete_record(self):
        index = main_win.table.currentRow()
        stud_id = main_win.table.item(index, 0).text()
        connection = Database().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", stud_id)
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh The Table
        main_win.load_table()

        self.close()

        conformation_message = QMessageBox()
        conformation_message.setWindowTitle("Success")
        conformation_message.setText("Record has been Deleted Successfully!")
        conformation_message.exec()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText("Enter The Name...")
        layout.addWidget(self.name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        student_name = self.name.text()
        connection = Database().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (student_name,))
        result = cursor.fetchall()
        rows = list(result)
        items = main_win.table.findItems(student_name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_win.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()
        self.close()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.id = QLineEdit()
        self.id.setPlaceholderText("Enter The Student ID...")
        layout.addWidget(self.id)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Enter Name...")
        layout.addWidget(self.name)

        self.course_name = QComboBox()
        courses = ["Biology", "Maths", "Physics", "Chemistry"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.mobile_nr = QLineEdit()
        self.mobile_nr.setPlaceholderText("Enter Mobile Number...")
        layout.addWidget(self.mobile_nr)

        submit = QPushButton("Submit")
        submit.clicked.connect(self.add_student)
        layout.addWidget(submit)

        self.setLayout(layout)

    def add_student(self):
        id_nr = self.id.text()
        name = self.name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile_nr = self.mobile_nr.text()

        connection = Database().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (id, name, course, mobile_nr) VALUES (%s,%s,%s,%s)",
                       (id_nr, name, course, mobile_nr))
        connection.commit()
        cursor.close()
        connection.close()
        main_win.load_table()
        self.close()


app = QApplication(sys.argv)
main_win = MainWindow()
main_win.load_table()
main_win.show()
sys.exit(app.exec())
