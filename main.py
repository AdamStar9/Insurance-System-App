import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, \
    QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt

from DatabaseConnection import DatabaseConnection


class MainWindow(QMainWindow):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("Insurance Management System")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_insurance_action = QAction(QIcon("icons/add.png"), "Add Record",
                                       self)
        add_insurance_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_insurance_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_insurance_action = QAction(QIcon("icons/search.png"),
                                          "Search Record", self)
        search_insurance_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_insurance_action)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ("id", "Name", "Insurance", "Mobile", "Age"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_insurance_action)
        toolbar.addAction(search_insurance_action)

        # Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        """

        :return:
        """
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

    def load_data(self):
        """

        :return:
        """
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM insurance")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number,
                                   QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert New Insurance")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add insurance name widget
        self.insurance_name = QLineEdit()
        self.insurance_name.setPlaceholderText("Name")
        layout.addWidget(self.insurance_name)

        # Add combo box of courses
        self.insurance = QComboBox()
        courses = ["Life Insurance", "Car Insurance", "House Insurance"]
        self.insurance.addItems(courses)
        layout.addWidget(self.insurance)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add age widget
        self.age = QLineEdit()
        self.age.setPlaceholderText("Age")
        layout.addWidget(self.age)

        # Add a submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_insurance)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_insurance(self):
        name = self.insurance_name.text()
        course = self.insurance.itemText(self.insurance.currentIndex())
        mobile = self.mobile.text()
        age = self.age.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO insurance "
                       "(name, course, mobile, age) VALUES (?, ?, ?, ?)",
                       (name, course, mobile, age))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Record Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add insurance name widget
        self.insurance_name = QLineEdit()
        self.insurance_name.setPlaceholderText("Name")
        layout.addWidget(self.insurance_name)

        # Create button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.insurance_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM insurance WHERE name = ?",
                                (name,))
        rows = list(result)
        print(rows)
        items = main_window.table.findItems(name,
                                            Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Record Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        # Get insurance name from selected row
        index = main_window.table.currentRow()
        insurance_name = main_window.table.item(index, 1).text()
        # Get id from selected row

        self.insurance_id = main_window.table.item(index, 0).text()

        # Add students name widget
        self.insurance_name = QLineEdit(insurance_name)
        self.insurance_name.setPlaceholderText("Name")
        layout.addWidget(self.insurance_name)

        # Add combo box of courses
        course_name = main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Life Insurance", "Car Insurance", "House Insurance"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Add mobile widget
        mobile = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add age widget
        age = main_window.table.item(index, 4).text()
        self.age = QLineEdit(age)
        self.age.setPlaceholderText("Age")
        layout.addWidget(self.age)

        # Add a submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_insurance)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_insurance(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE insurance SET name = ?, course = ?, mobile = ?, age = ? "
            "WHERE id =?",
            (self.insurance_name.text(),
             self.course_name.itemText(self.course_name.currentIndex()),
             self.mobile.text(),
             self.age.text(),
             self.insurance_id))
        connection.commit()
        cursor.close()
        connection.close()
        # Refresh the table
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Record Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_record)

    def delete_record(self):
        # Get selected row index and insurance id
        index = main_window.table.currentRow()
        insurance_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from insurance WHERE id = ?", (insurance_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during the course 
        "IT Network - Python Programator".
        
        """

        self.setText(content)


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
