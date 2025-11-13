#Импорт необходимых для приложения модулей
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from main import Ui_MainWindow
from parser import Parser
from modal import Modal
from fileDialog import FileDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__initUi()
        """
            Инициализируем общие для всего класса поля. 
            Поле self.solutions хранит результат парсинга.
            Поле self.fileDialog хранит экземпляр класса для сохранения резульаттов парсинга
        """
        self.solutions = None
        self.fileDialog = FileDialog()

    def __initUi(self):
        # Инициализация графического интерфейса, подключение обработчиков событий для кнопок.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(1020, 694)
        self.ui.save_results_button.setEnabled(False)
        self.ui.parse_button.clicked.connect(self.__checkInput)
        self.ui.save_results_button.clicked.connect(self.__save_file)
        self.ui.show_statistic_button.clicked.connect(self.__show_statistic)

    def __checkInput(self):
        # Проверка корректности ввода (наличия текста в текстовом поле).
        self.problem_text = self.ui.problem_input.text().strip()
        if self.problem_text == "":
            self.ui.control_label.setText("Пожалуйста, введите текст проблемы!")
        else:
            self.__start_parsing()
            
    def __start_parsing(self):
        # Функция начала парсинга. 
        # Для парсинга создается отдельный поток, с последуюущим удалением, для того, чтобы во время сетевых запросов не блокировалось основное окно.
        try:
            self.parser_thread = QtCore.QThread()
            self.parser = Parser(self.problem_text)
            self.parser.moveToThread(self.parser_thread)
            self.parser_thread.started.connect(self.parser.run)
            self.parser.done.connect(self.__go_to_results)
            self.parser.failed.connect(self.__on_parsing_failed)
            self.parser.finished.connect(self.parser_thread.quit)
            self.parser.finished.connect(self.parser.deleteLater)
            self.parser_thread.finished.connect(self.parser_thread.deleteLater)
            self.ui.parse_button.setEnabled(False)
            self.ui.save_results_button.setEnabled(False)
            self.ui.show_statistic_button.setEnabled(False)
            self.parser_thread.start()
        except Exception as e:
            print("Ошибка в методе start_parsing: ", e)

    def __go_to_results(self, response_fromParser):
        # Метод выводит на главное окно информацию о статусе запроса и когда этап 3/3 мы разблокируем кнопки GUI и сохраним решения запроса
        self.ui.control_label.setText(f"Этап {response_fromParser['stage']}/3 - {response_fromParser['text']}")
        if response_fromParser['stage'] == 3:
            self.solutions = response_fromParser['solutions']
            self.ui.parse_button.setEnabled(True)
            self.ui.save_results_button.setEnabled(True)
            self.ui.show_statistic_button.setEnabled(True)
    
    def __on_parsing_failed(self):
        # Метод обрабатывает ошибочное проведение парсинга
        self.ui.control_label.setText("Ошибка парсинга! см. логи.")
        self.ui.parse_button.setEnabled(True)
        self.ui.show_statistic_button.setEnabled(True)

    def __save_file(self):
        # Метод сохраняет результаты парсинга в текстовый файл
        self.fileDialog.saveFile(self.problem_text, self.solutions)

    def __show_statistic(self):
        #Функция показывающая диалоговое окно с столбчатой диаграммой в отдельном диалоговом окне.
        try:
            dlg_statistic = Modal(self)
            dlg_statistic.exec()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)