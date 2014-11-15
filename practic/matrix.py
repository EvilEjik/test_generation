from itertools import cycle
from random import randint, random

from practic.models import MatrixQuestion
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
    for i in range(0, size):
        row = []
        for j in range(0, size):
            row.append(randint(-10, 50))
        matrix.append(row)

    matrix_lesson.matrix = matrix
    matrix_lesson.save()
    for i in range(matrix_lesson.number_of_questions):
        current = next(cycled_question_list)
        matrix_question = MatrixQuestion.objects.create(lesson=practical_lesson_result)

        #Вопросы с поиском наибольшего/наименьшего элемента в матрице и его координат
        if current == 'search':
            matrix_question.question_text = "Напишите программу для поиска значения и координат"
            matrix_question.question_code = "matrix=" + str(matrix) + "\nresult = [0,0,0]\n"
            if random() > 0.5:
                matrix_question.question_text += " минимального "
                max_min = "\t\tif result[0] > matrix[i][j]:\n"
            else:
                matrix_question.question_text += " максимального "
                max_min = "\t\tif result[0] < matrix[i][j]:\n"
            matrix_question.question_text += " элемента в "
            r = random()
            if r >= 0.55:
                matrix_question.question_text += "матрице"
                matrix_question.question_code += \
                    "for i in range(0, len(matrix)):\n\tfor j in range(0, len(matrix)):\n"
            elif 0.25 < r < 0.55:
                row = randint(1, size)
                matrix_question.question_text += "строке " + str(row)
                matrix_question.question_code += \
                    "for i in range(" + str(row-1) + "," + str(row) + "):\n\tfor j in range(0, len(matrix)):\n"
            else:
                col = randint(1, size)
                matrix_question.question_text += "столбце " + str(col)
                matrix_question.question_code += \
                    "for i in range(0, len(matrix)):\n\tfor j in range(" + str(col-1) + "," + str(col) + "):\n"
            matrix_question.question_code += max_min
            matrix_question.question_code += \
                "\t\t\tresult[0] = matrix[i][j]\n\t\t\tresult[1] = i + 1\n\t\t\tresult[2] = j + 1"
            matrix_question.question_code += "\nprint(result)"
            matrix_question.question_text += " (В виде списка [значение, номер строки, номер столбца], Первое вхождение)"
            matrix_question.answer, err = run_code(str(practical_lesson_result.id), matrix_question.question_code)
            matrix_question.save()

        #Вопросы с обходом матрицы как верхне/нижнетреугольной с подсчетами
        elif current == 'traversal':
            matrix_question.question_text = "Напишите программу по обходу матрицы как"
            r = random()
            if 0.25 < r < 0.55:
                result = 1
            else:
                result = 0
            matrix_question.question_code = \
                "matrix=" + str(matrix) + "\nresult=" + str(result) + "\nfor i in range(0, len(matrix)):\n"
            if random() > 0.5:
                matrix_question.question_text += " верхнетреугольной "
                matrix_question.question_code += "\tfor j in range(i, len(matrix)):\n"
            else:
                matrix_question.question_text += " нижнетреугольной "
                matrix_question.question_code += "\tfor j in range(0, i):\n"
            matrix_question.question_text += "с подсчетом "
            if r >= 0.55:
                matrix_question.question_text += "суммы квадратов "
                matrix_question.question_code += "\t\tresult+=matrix[i][j]*matrix[i][j]\n"
            elif 0.25 < r < 0.55:
                matrix_question.question_text += "произведения "
                matrix_question.question_code += "\t\tresult*=matrix[i][j]\n"
            else:
                matrix_question.question_text += "суммы кубов "
                matrix_question.question_code += "\t\tresult+=matrix[i][j]*matrix[i][j]*matrix[i][j]\n"

            matrix_question.question_code += "print(result)"
            matrix_question.question_text += "элементов"
            matrix_question.answer, err = run_code(str(practical_lesson_result.id), matrix_question.question_code)
            matrix_question.save()

        #Вопросы на установление соответствия между элементами столбцов/строк
        elif current == 'interaction':
            value = randint(6000, 9000)
            row = False
            matrix_question.question_text = "Напишите программу поиска в матрице "
            matrix_question.question_code = "matrix=" + str(matrix) + \
                                            "\nvalue="+str(value)+"\nresult=[]\nfor i in range(0, len(matrix)):\n"
            if random() > 0.5:
                row = True
                matrix_question.question_text += "столбцов, "
                matrix_question.question_code += "\ttemp=1\n\tfor j in range(0, len(matrix)):\n"
            else:
                matrix_question.question_text += "строк, "
                matrix_question.question_code += "\ttemp=1\n\tfor j in range(0, len(matrix)):\n"
            matrix_question.question_text += "в которых "
            r = random()
            if r >= 0.55:
                matrix_question.question_text += "сумма квадратов "
                if row:
                    matrix_question.question_code += "\t\ttemp+=matrix[j][i]*matrix[j][i]\n"
                else:
                    matrix_question.question_code += "\t\ttemp+=matrix[i][j]*matrix[i][j]\n"
            elif 0.25 < r < 0.55:
                matrix_question.question_text += "произведение "
                if row:
                    matrix_question.question_code += "\t\ttemp*=matrix[j][i]\n"
                else:
                    matrix_question.question_code += "\t\ttemp*=matrix[i][j]\n"
            else:
                matrix_question.question_text += "сумма "
                if row:
                    matrix_question.question_code += "\t\ttemp+=matrix[j][i]\n"
                else:
                    matrix_question.question_code += "\t\ttemp+=matrix[i][j]\n"

            matrix_question.question_text += "всех элементов будет "
            if random() > 0.5:
                matrix_question.question_text += "больше или равна " + str(value)
                if row:
                    matrix_question.question_code += "\tif temp >= value:\n\t\tresult.append(i)\n"
                else:
                    matrix_question.question_code += "\tif temp >= value:\n\t\tresult.append(i)\n"
            else:
                matrix_question.question_text += "меньше или равна " + str(value)
                if row:
                    matrix_question.question_code += "\tif temp <= value:\n\t\tresult.append(j)\n"
                else:
                    matrix_question.question_code += "\tif temp <= value:\n\t\tresult.append(i)\n"

            matrix_question.question_text += " (Ответ дать в виде списка упорядоченных по возрастанию номеров векторов)"
            matrix_question.question_code += "\nprint(result)"
            matrix_question.answer, err = run_code(str(practical_lesson_result.id), matrix_question.question_code)
            matrix_question.save()

        #Вопросы на сортировку матрицы по элементам столбца/строки
        else:
            matrix_question.question_text = "Напишите программу для сортировки элементов матрицы по элементам "
            matrix_question.question_code = "from operator import itemgetter\nmatrix=" + str(matrix) + "\n"
            value = randint(0, size)
            r = random()
            if r > 0.5:
                matrix_question.question_text += str(value) + " столбца "
            else:
                matrix_question.question_text += str(value) + " строки "
                matrix_question.question_code += "matrix = zip(*matrix)\n"

            matrix_question.question_code += "matrix = sorted(matrix, key=itemgetter(" + str(value)
            if random() > 0.5:
                matrix_question.question_text += "по возрастанию"
                matrix_question.question_code += "))\n"
            else:
                matrix_question.question_text += "по убыванию "
                matrix_question.question_code += "), reverse=True)\n"
            if r < 0.5:
                matrix_question.question_code += "matrix = list(zip(*matrix))\n"
                matrix_question.question_code += \
                    "for i in range(len(matrix)):\n\tmatrix[i] = list(matrix[i][:])\n"
            matrix_question.question_code += "print(matrix)"
            matrix_question.question_text += " (В виде списка списков по строкам)"
            matrix_question.answer, err = run_code(str(practical_lesson_result.id), matrix_question.question_code)
            matrix_question.save()