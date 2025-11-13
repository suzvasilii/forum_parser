from PyQt5.QtWidgets import QFileDialog

class FileDialog:
    def __init__(self):
        self.filename = None

    def saveFile(self, problem_text, solutions):
        # Метод для внешнего вызова
        self.problem_text = problem_text
        self.solutions = solutions
        self.__save_file()

    def __save_file(self):
        # Метод для сохранения результатов парсинга в файл, с именем, который ввел пользователь в QFileDialog
        
        # Данная конструкция if-else по умолчанию выбириает имя для файла results.txt. 
        # В случае если результат парсинга уже сохранялся, метод берет прошлое имя файла для установки по умолчанию.
        if self.filename: directory = self.filename
        else: directory = "results.txt"
        path = QFileDialog.getSaveFileName(filter="Текстовые файлы (*.txt)", directory=f"{directory}")
        # Т.к. QFileDialog возвращает массив данных, где первым элементом является имя файла, которое ввел пользователь, мы его декомпозируем.
        self.filename= path[0]
        # Попытка сохранить результат парсинга в файл с обработкой ошибок.
        try:
            with open(path[0], 'a', encoding='utf-8') as file:
                file.write(f"Вопрос: {self.problem_text}\n")
                file.write("Ответы с хабра\n")
                if len(self.solutions["habr"]) > 0:
                    for h in self.solutions["habr"]:
                        file.write(f'{h}\n')
                else:
                    file.write("Нет ответов на данный вопрос. \n")
                if len(self.solutions["stack_overflow"]) > 0:
                    file.write("Ответы с stack_overflow\n")
                    for s in self.solutions["stack_overflow"]:
                        file.write(f'{s}\n')
                else:
                    file.write("Нет ответов на данный вопрос. \n\n")
            print("Файл успешно сохранен!")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")