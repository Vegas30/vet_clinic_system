from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.ui_animals_widget import AnimalsWidget
from ui.ui_appointments_widget import AppointmentsWidget
from ui.ui_branch_widget import BranchWidget
# from ui.ui_staff_widget import StaffWidget
# from ui.ui_reports_widget import ReportsWidget

class MainWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle(f"Ветеринарная клиника - {user_data['role']}: {user_data['full_name']}")
        self.setGeometry(100, 100, 1024, 768)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.init_tabs()

    def init_tabs(self):
        # Вкладка Животные
        self.animals_widget = AnimalsWidget()
        self.tab_widget.addTab(self.animals_widget, "Животные")

        # Вкладка Приёмы
        self.appointments_widget = AppointmentsWidget(self.user_data)
        self.tab_widget.addTab(self.appointments_widget, "Приёмы")
        self.appointments_widget.data_updated.connect(self.handle_appointments_update)

        # Вкладка Сотрудники
        # self.staff_widget = StaffWidget()
        # self.tab_widget.addTab(self.staff_widget, "Сотрудники")
        self.staff_widget = QWidget()
        self.tab_widget.addTab(self.staff_widget, "Сотрудники")

        # Вкладка Филиалы
        self.branch_widget = BranchWidget()
        self.tab_widget.addTab(self.branch_widget, "Филиалы")
        # self.branch_widget = QWidget()
        # self.tab_widget.addTab(self.branch_widget, "Филиалы")

        # if self.user_data['role'] == 'admin':
        #     self.staff_widget = StaffWidget(self.user_data)
        #     self.tab_widget.addTab(self.staff_widget, "Сотрудники")
        # else:
        #     # Для не-админов скрываем вкладку сотрудников
        #     self.staff_widget = None


        # Вкладка Отчёты
        # self.reports_widget = ReportsWidget()
        # self.tab_widget.addTab(self.reports_widget, "Отчёты")
        self.reports_widget = QWidget()
        self.tab_widget.addTab(self.reports_widget, "Отчёты")

    def handle_appointments_update(self):
        """Обновляет данные после изменений в приёмах"""
        self.appointments_widget.load_appointments()
