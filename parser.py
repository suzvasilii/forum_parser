#Импортируем необходимые модули
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
import os
import bs4
import pandas as pd
from urllib.parse import unquote
import requests
import time

class Parser(QObject):
    # Подключение сигналов для общения с основым потоком программы.
    done = pyqtSignal(object)
    failed = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, problem_text):
        super().__init__()
        self.problem_text = problem_text
        # Инициализиуем self.response, возвращающий ответ по парсингу в основной поток и self.problem_solutions
        self.response = {
            "stage":None,
            "text":None,
            "solutions": None
        }
        self.problem_solutions = {
            "habr":[],
            "stack_overflow":[]
        }

    @pyqtSlot()
    def run(self):
        # Создаем ссылки для парсинга
        habr_link = f'https://qna.habr.com/search/questions?q={self.problem_text}&a=1&s=1&t=0'
        stack_overflow_link = f'https://ru.stackoverflow.com/search?q={self.problem_text}+isaccepted%3Ayes'
        try:
            # Возвращаем статус выполения запроса в главное окно, выполняем сетевые завпросы, создаем искусственную задержку
            self.response["stage"] = 1
            self.response["text"] = "Идет выполенение сетевых запросов"
            self.done.emit(self.response)
            self.__get_answers(site="HABR", url=habr_link, solutions=self.problem_solutions["habr"])
            self.__get_answers(site="STACK_OVERFLOW", url=stack_overflow_link, solutions=self.problem_solutions["stack_overflow"])
            time.sleep(3)
            # Возвращаем статус сохранения файла статистики в главное окно, выполняем сохранение, создаем искусственную задержку
            self.response["stage"] = 2
            self.response["text"] = "Идет сохранение файла статистики"
            self.done.emit(self.response)
            self.__save_statistic()
            time.sleep(2)
            # Возращаем успешное завершение в главный поток и передаем решения по проблеме
            self.response["stage"] = 3
            self.response["text"] = "Успех!"
            self.response["solutions"] = self.problem_solutions
            self.done.emit(self.response)
        except Exception as e:
            print("При парсинге произошла внутренняя ошибка в слоте: ", e)
            self.failed.emit()
        finally:
            self.finished.emit()

    def __get_answers(self, site, url,solutions):
        # Функция для сетевых запросов
        # Проверка, что site находится в допустимых именах сайтов. 
        if site in ["HABR", "STACK_OVERFLOW"]:
            # Инициализация переменных domen и prefix.
            # domen хранит строку, где записано доменное имя ресурса.
            # posfix хранит якорную ссылку на ответ на заданный вопрос.
            # Данные переменные созданы ввиду того, что у habr и stack_overflow немного разная html конструкция.
            domen =""
            postfix = ""
            if site == "HABR":
                solution_link_classes = "question__title-link"
                postfix="#solutions"
            else:
                solution_link_classes = "answer-hyperlink"
                domen ="https://ru.stackoverflow.com"
            #Создание сессии для сетевого запроса.
            session = requests.Session()
            session.headers.update({
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36",
                "Accept":"text/html"
            })
            try:
                response = session.get(url, timeout=10)
                if response.status_code == 200:
                    print("Запрос прошел успешно!")
                    # В случае успеха мы получаем html код с тикетами по данному запросу.
                    html = bs4.BeautifulSoup(response.text, 'lxml')
                    solution_links = html.find_all("a", class_=solution_link_classes)
                    # В случае успеха в переданный список solutions в конец добавляются строки, с гиперссылкой на ответ, в каждом найденном тикете.
                    for link in solution_links:
                        decoded_link = unquote(link.get('href'))
                        solutions.append(f'{domen}{decoded_link}{postfix}')
                else:
                    print(response.status_code)
            except Exception as e:
                print(e)
            # В конце запроса закрываем сессию.
            session.close()
    
    def __save_statistic(self):
        # Функция для сохранения стастики количества найденных ответов на ресурсах.
        # Если файл statistic.xlsx уже сущетвует мы берем предыдущие данные и прибавляем к ним результаты текущего запроса.
        try:
            if os.path.exists('statistic.xlsx'):
                df = pd.read_excel("statistic.xlsx", header=0)
                count_answers = df.iloc[0].tolist()
                data = {
                    "Habr":count_answers[0] + len(self.problem_solutions["habr"]),
                    "Stack_overflow":count_answers[1] + len(self.problem_solutions["stack_overflow"])
                }
            else:
                data = {
                    "Habr":len(self.problem_solutions["habr"]),
                    "Stack_overflow":len(self.problem_solutions["stack_overflow"])
                }
            df = pd.DataFrame([data])
            df.to_excel('statistic.xlsx', index=False)
        except Exception as e:
            print("Ошибка при сохранении статистики в методе save_statistic: ", e)
