import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QGroupBox, QDialog, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QThread, pyqtSignal

class ListContainersWorker(QThread):
    data_updated = pyqtSignal(list)

    def run(self):
        while True:
            command = "distrobox-list --no-color"
            output = subprocess.getoutput(command)
            data = self.parse_output(output)
            self.data_updated.emit(data)

    def parse_output(self, output):
        lines = output.split("\n")
        data = []

        for line in lines[1:]:  # Skip the header line
            columns = line.split(" | ")
            data.append([item.strip() for item in columns])

        return data

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DistroHub(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DistroHub")
        self.setGeometry(100, 100, 600, 200)

        # Initialize the dictionary for distros and container URLs
        self.distros = {
            'Select Distro': '',  # Placeholder value for the first option
            'Ubuntu': 'ubuntu:latest',
            'Debian': 'debian:latest',
        }

        self.initUI()

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Create "Create" section
        create_groupbox = QGroupBox("Create")
        create_layout = QVBoxLayout(create_groupbox)
        self.create_section(create_layout)
        main_layout.addWidget(create_groupbox)

        # Create "Manage" section
        manage_groupbox = QGroupBox("Manage")
        manage_layout = QVBoxLayout(manage_groupbox)
        self.manage_section(manage_layout)
        main_layout.addWidget(manage_groupbox)

        # Initialize and start the worker thread for container list update
        self.list_containers_worker = ListContainersWorker()
        self.list_containers_worker.data_updated.connect(self.update_list_containers)
        self.list_containers_worker.start()

    def create_section(self, layout):
        self.name_textbox = QLineEdit()
        self.name_textbox.setPlaceholderText("Enter Name")

        self.distro_dropdown = QComboBox()
        distro_options = list(self.distros.keys())  # Use the keys of the self.distros dictionary
        self.distro_dropdown.addItems(distro_options)
        self.distro_dropdown.setCurrentIndex(0)

        self.create_button = QPushButton("Create Container")
        self.create_button.clicked.connect(self.create_container)

        layout.addWidget(self.name_textbox)
        layout.addWidget(self.distro_dropdown)
        layout.addWidget(self.create_button)

    def manage_section(self, layout):
        # List Containers button
        self.list_containers_button = QPushButton("List Containers")
        self.list_containers_button.clicked.connect(self.show_list_containers_popup)
        layout.addWidget(self.list_containers_button)

    def create_container(self):
        container_name = self.name_textbox.text()
        selected_distro = self.distro_dropdown.currentText()

        if selected_distro == "Select Distro":
            self.show_error_popup("Please choose a distro first.")
            return

        container_url = self.get_container_url(selected_distro)

        command = f'distrobox-create --image "{container_url}" --name "{container_name}" --nvidia --yes'
        print(f"Executing command: {command}")

        output = subprocess.getoutput(command)
        if "Distrobox named '{}' already exists.".format(container_name) in output:
            self.show_info_popup(f"Distrobox named '{container_name}' already exists.\nTo enter, run:\n\ndistrobox enter {container_name}")
        elif "successfully created" in output:
            self.show_info_popup(f"Distrobox named '{container_name}' successfully created.")
            print(output)
        else:
            self.show_error_popup(f"Failed to create Distrobox named '{container_name}'.")
            print(output)

    def get_container_url(self, selected_distro):
        # Get the container URL from the self.distros dictionary
        return self.distros[selected_distro]

    def show_error_popup(self, message):
        error_popup = QMessageBox()
        error_popup.setWindowTitle("Error")
        error_popup.setText(message)
        error_popup.setIcon(QMessageBox.Critical)
        error_popup.exec_()

    def show_info_popup(self, message):
        info_popup = QMessageBox()
        info_popup.setWindowTitle("Info")
        info_popup.setText(message)
        info_popup.setIcon(QMessageBox.Information)
        info_popup.exec_()

    def show_list_containers_popup(self):
        popup = ListContainersPopup(self.list_containers_worker)
        popup.show()

    def update_list_containers(self, data):
        popup = self.findChild(ListContainersPopup)
        if popup:
            popup.update_table(data)

class ListContainersPopup(metaclass=SingletonMeta):
    def __init__(self, worker):
        self.dialog = QDialog()
        self.dialog.setWindowTitle("List Containers")
        self.dialog.setGeometry(100, 100, 800, 400)
        self.initUI()

        self.worker = worker
        self.worker.data_updated.connect(self.update_table)

    def initUI(self):
        layout = QVBoxLayout(self.dialog)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Set up table headers
        headers = ["ID", "NAME", "STATUS", "MEM", "CPU%", "IMAGE"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

    def update_table(self, data):
        self.table.setRowCount(len(data))

        for row, item in enumerate(data):
            for col, value in enumerate(item):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def show(self):
        self.dialog.show()

    def exec_(self):
        self.dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DistroHub()
    window.show()
    sys.exit(app.exec_())
