#Импортируем необходимые модули
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
import pyqtgraph as pg
import pandas as pd

class Modal(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.__initUi()
        self.__show_statistic()
    
    def __initUi(self):
        #Инициализация GUI модального окна.
        self.setWindowTitle("Статистика количества ответов")
        self.setFixedSize(600, 400)
        self.graph = pg.PlotWidget()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        layout = QVBoxLayout()
        layout.addWidget(self.graph)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
    
    def __show_statistic(self):
        # Функция для отображения столбчатой диаграммы, отражающей количество ответов на запросы за все время.
        habr, stack = self.__load_data()
        categories = ['Habr', 'Stack Overflow']
        bar_graph = pg.BarGraphItem(x=0, height = habr, width = 0.6, brush="g")
        bar2_graph = pg.BarGraphItem(x=1, height = stack, width = 0.6, brush="b")
        self.graph.addItem(bar_graph)
        self.graph.addItem(bar2_graph)
        self.graph.setLabel('left', 'Количество ответов')
        self.graph.setLabel('bottom', 'Платформы')
        self.graph.setTitle('Общая статистика найденных ответов')
        self.graph.getAxis('bottom').setTicks([[(i, categories[i]) for i in range(len(categories))]])

    def __load_data(self):
        # Попытка чтения файла statistic.xlsx
        try:
            df = pd.read_excel("statistic.xlsx", header=0)
            count = df.iloc[0].tolist()
            return count
        except Exception as e:
            print("Ошибка при чтении файла в методе load_data: ", e)
            return [0,0]
        