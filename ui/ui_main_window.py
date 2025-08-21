# ui_main_window.py
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.ui_animals_widget import AnimalsWidget
from ui.ui_appointments_widget import AppointmentsWidget
from ui.ui_branch_widget import BranchWidget
# from ui.ui_staff_widget import StaffWidget
from ui.ui_reports_widget import ReportsWidget
from ui.ui_services_widget import ServicesWidget

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

        # Отключаем старые соединения перед созданием новых
        try:
            self.appointments_widget.data_updated.disconnect()
        except:
            pass
        self.appointments_widget.data_updated.connect(self.handle_data_update)

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
        self.reports_widget = ReportsWidget(self.user_data)
        self.tab_widget.addTab(self.reports_widget, "Отчёты")
        # bf.tab_widget.addTab(self.reports_widget, "Отчёты")

        # Вкладка Услуги
        self.services_widget = ServicesWidget(self.user_data)
        self.tab_widget.addTab(self.services_widget, "Услуги")

        # Отключаем старые соединения перед созданием новых
        try:
            self.services_widget.data_updated.disconnect()
        except:
            pass
        self.services_widget.data_updated.connect(self.handle_data_update)

    def handle_data_update(self):
        """Обновляет данные во всех виджетах при изменении"""
        # Добавляем проверку, чтобы избежать рекурсии
        if not hasattr(self, '_updating'):
            self._updating = True
            try:
                self.animals_widget.load_all_animals()
                self.appointments_widget.load_appointments()
                self.services_widget.load_services()
            finally:
                del self._updating
