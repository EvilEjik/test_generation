from itertools import cycle
from random import randint, random

from practic.models import CodeQuestion
from main.views import run_code


def matrix_preparation(matrix_lesson, practical_lesson_result):
    questions = []
    if matrix_lesson.search_value_question:
        questions.append('search')
    if matrix_lesson.interaction_question:
        questions.append('interaction')
    if matrix_lesson.sort_question:
        questions.append('sort')
    if matrix_lesson.matrix_traversal_question:
        questions.append('traversal')

    cycled_question_list = cycle(questions)
    matrix = []
    size = randint(10, 25)
    for i in range(size):
        row = []
        for j in range(size):
            row.append(randint(-10, 50))
        matrix.append(row)

    matrix_lesson.matrix = matrix
    matrix_lesson.save()
    for i in range(matrix_lesson.number_of_questions):
        current = next(cycled_question_list)
        matrix_question = CodeQuestion.objects.create(lesson=practical_lesson_result)

        #Вопросы с поиском наибольшего/наименьшего элемента в матрице и его координат
        if current == 'search':
            question_text = ["Напишите программу для поиска значения и координат"]
            question_code = ["matrix=" + str(matrix) + "\nresult = [0,0,0]\n"]
            if random() > 0.5:
                question_text.append(" минимального ")
                max_min = "\t\tif result[0] > matrix[i][j]:\n"
            else:
                question_text.append(" максимального ")
                max_min = "\t\tif result[0] < matrix[i][j]:\n"
            question_text.append(" элемента в ")
            r = random()
            if r >= 0.55:
                question_text.append("матрице")
                question_code.append("for i in range(0, len(matrix)):\n\tfor j in range(0, len(matrix)):\n")
            elif 0.25 < r < 0.55:
                row = randint(1, size)
                question_text.append("строке " + str(row))
                question_code.append(
                    "for i in range(" + str(row-1) + "," + str(row) + "):\n\tfor j in range(0, len(matrix)):\n")
            else:
                col = randint(1, size)
                question_text.append("столбце " + str(col))
                question_code.append("for i in range(0, len(matrix)):\n\tfor j in range(" + str(col-1) + "," +
                                     str(col) + "):\n")
            question_code.append(max_min)
            question_code.append("\t\t\tresult[0] = matrix[i][j]\n\t\t\tresult[1] = i + 1\n\t\t\tresult[2] = j + 1")
            question_code.append("\nprint(result)")
            question_text.append("( В виде списка [значение, номер строки, номер столбца], Первое вхождение)")

        #Вопросы с обходом матрицы как верхне/нижнетреугольной с подсчетами
        elif current == 'traversal':
            question_text = ["Напишите программу по обходу матрицы как"]
            r = random()
            if 0.25 < r < 0.55:
                result = 1
            else:
                result = 0
            question_code = ["matrix=" + str(matrix) + "\nresult=" + str(result) + "\nfor i in range(0,len(matrix)):\n"]
            if random() > 0.5:
                question_text.append(" верхнетреугольной ")
                question_code.append("\tfor j in range(i, len(matrix)):\n")
            else:
                question_text.append(" нижнетреугольной ")
                question_code.append("\tfor j in range(0, i):\n")
            question_text.append("с подсчетом ")
            if r >= 0.55:
                question_text.append("суммы квадратов ")
                question_code.append("\t\tresult+=matrix[i][j]*matrix[i][j]\n")
            elif 0.25 < r < 0.55:
                question_text.append("произведения ")
                question_code.append("\t\tresult*=matrix[i][j]\n")
            else:
                question_text.append("суммы кубов ")
                question_code.append("\t\tresult+=matrix[i][j]*matrix[i][j]*matrix[i][j]\n")

            question_code.append("print(result)")
            question_text.append("элементов")

        #Вопросы на установление соответствия между элементами столбцов/строк
        elif current == 'interaction':
            value = randint(6000, 9000)
            row = False
            question_text = ["Напишите программу поиска в матрице "]
            question_code = [
                "matrix=" + str(matrix) + "\nvalue=" + str(value) + "\nresult=[]\nfor i in range(0, len(matrix)):\n"]
            if random() > 0.5:
                row = True
                question_text.append("столбцов, ")
                question_code.append("\ttemp=1\n\tfor j in range(0, len(matrix)):\n")
            else:
                question_text.append("строк, ")
                question_code.append("\ttemp=1\n\tfor j in range(0, len(matrix)):\n")
            question_text.append("в которых ")
            r = random()
            if r >= 0.55:
                question_text.append("сумма квадратов ")
                if row:
                    question_code.append("\t\ttemp+=matrix[j][i]*matrix[j][i]\n")
                else:
                    question_code.append("\t\ttemp+=matrix[i][j]*matrix[i][j]\n")
            elif 0.25 < r < 0.55:
                question_text.append("произведение ")
                if row:
                    question_code.append("\t\ttemp*=matrix[j][i]\n")
                else:
                    question_code.append("\t\ttemp*=matrix[i][j]\n")
            else:
                question_text.append("сумма ")
                if row:
                    question_code.append("\t\ttemp+=matrix[j][i]\n")
                else:
                    question_code.append("\t\ttemp+=matrix[i][j]\n")

            question_text.append("всех элементов будет ")
            if random() > 0.5:
                question_text.append("больше или равна " + str(value))
                if row:
                    question_code.append("\tif temp >= value:\n\t\tresult.append(i)\n")
                else:
                    question_code.append("\tif temp >= value:\n\t\tresult.append(i)\n")
            else:
                question_text.append("меньше или равна " + str(value))
                if row:
                    question_code.append("\tif temp <= value:\n\t\tresult.append(j)\n")
                else:
                    question_code.append("\tif temp <= value:\n\t\tresult.append(i)\n")

            question_text.append(" (Ответ дать в виде списка упорядоченных по возрастанию номеров векторов)")
            question_code.append("\nprint(result)")

        #Вопросы на сортировку матрицы по элементам столбца/строки
        else:
            question_text = ["Напишите программу для сортировки элементов матрицы по элементам "]
            question_code = ["from operator import itemgetter\nmatrix=" + str(matrix) + "\n"]
            value = randint(0, size)
            r = random()
            if r > 0.5:
                question_text.append(str(value) + " столбца ")
            else:
                question_text.append(str(value) + " строки ")
                question_code.append("matrix = zip(*matrix)\n")

            question_code.append("matrix = sorted(matrix, key=itemgetter(" + str(value))
            if random() > 0.5:
                question_text.append("по возрастанию")
                question_code.append("))\n")
            else:
                question_text.append("по убыванию ")
                question_code.append("), reverse=True)\n")
            if r < 0.5:
                question_code.append("matrix = list(zip(*matrix))\n")
                question_code.append(
                    "for i in range(len(matrix)):\n\tmatrix[i] = list(matrix[i][:])\n")

            question_code.append("print(matrix)")
            question_text.append(" (В виде списка списков по строкам)")

        question_code = ''.join(question_code)
        question_text = ''.join(question_text)
        matrix_question.answer, err = run_code(str(practical_lesson_result.id), question_code)
        matrix_question.question_code = question_code
        matrix_question.question_text = question_text
        matrix_question.save()