import string
from itertools import cycle
from random import sample, randint, choice

from practic.models import CodeQuestion, SQLTable, SQLField
from main.views import run_sql


def sql_prepare(tables, question_type):
    select_part = list()
    from_part = list()
    where_part = list()
    select_part_text = list()
    where_part_text = list()

    select_part_error = list()
    from_part_error = list()
    where_part_error = list()

    first = True

    select_part.append('SELECT ')
    select_part_error.append('SELECT ')
    select_part_text.append('Выведите поля ')

    for table in tables:
        if first:
            from_part.append('FROM ' + table.table_name)
            from_part_error.append('FROM ' + table.table_name)
            where_part.append('Where ')
            where_part_error.append('Where ')
            where_part_text.append(' Где значение поля ')
            first = False
        fields = SQLField.objects.filter(table=table, is_relative=True)
        sample_f = SQLField.objects.filter(table=table, is_relative=False)
        selected_fields = sample(list(sample_f), len(sample_f)//2)
        original_selected_fields = selected_fields[:]
        select_part_text.append(', '.join(r.field_name for r in selected_fields))
        for index in range(len(selected_fields)):
            selected_fields[index] = table.table_name + '.' + selected_fields[index].field_name + ','
        select_part.append(' '.join(selected_fields))
        if question_type == 'search':
                select_part_error.append(' '.join(sample(selected_fields, len(sample_f)//3)))

        if original_selected_fields[0].data_type == 'Integer':
            value = str(randint(0, 20))
            operation = choice(['<', '>'])
            operation_text = ' меньше ' if operation == '<' else ' больше '
            where_part.append((selected_fields[0])[:-1] + operation + value + ' AND ')
            where_part_text.append((selected_fields[0])[:-1] + operation_text + value + ' ')
            if question_type == 'search':
                where_part_error.append((selected_fields[0])[:-1] + choice(['<', '>', '!=']) + value + ' AND ')
        elif original_selected_fields[0].data_type == 'Varchar(255)':
            value = str(choice(string.ascii_lowercase))
            where_part.append((selected_fields[0])[:-1] + " LIKE '%" + value + "%' AND ")
            where_part_text.append((selected_fields[0])[:-1] + ' содержит в себе  ' + value + ' ')
            if question_type == 'search':
                where_part_error.append((selected_fields[0])[:-1] + " LICE " + value + " AND ")
        elif original_selected_fields[0].data_type == 'Boolean':
            value = str(choice([True, False]))
            where_part.append((selected_fields[0])[:-1] + '=' + value + ' AND ')
            where_part_text.append((selected_fields[0])[:-1] + ' равно ' + value + ' ')
            if question_type == 'search':
                where_part_error.append((selected_fields[0])[:-1] + '!=' + value + ' AND ')

        for field in fields:
            from_part.append(' INNER JOIN ' + table.table_name)
            from_part_error.append(' INER JOIN ' + table.table_name)
            from_part.append(' ON ' + table.table_name + '.' + field.field_name + '=' + field.relation)
            from_part_error.append(' ON ' + table.table_name + ',' + field.field_name + '==' + field.relation)

    if question_type == 'write':
        question_text = ' '.join(select_part_text) + ' '.join(where_part_text)
        question_code = (' '.join(select_part))[:-1] + ' ' + ' '.join(from_part) + ' ' + ' '.join(where_part)[:-4] + ';'
    elif question_type == 'search':
        question_text = 'Исправьте ошибку в запросе, чтобы он соответствовал текстовой формулировке: '
        question_false_code = (' '.join(select_part_error))[:-1] + ' ' + ' '.join(from_part_error) + ' ' \
                              + ' '.join(where_part_error)[:-4] + ';'
        question_text += ' '.join(select_part_text) + ' '.join(where_part_text) + ' ' + question_false_code
        question_code = (' '.join(select_part))[:-1] + ' ' + ' '.join(from_part) + ' ' + ' '.join(where_part)[:-4] + ';'
    else:
        question_code = (' '.join(select_part))[:-1] + ' ' + ' '.join(from_part) + ' ' + ' '.join(where_part)[:-4] + ';'
        question_text = 'По данному запросу выпишите результат выдачи: ' + question_code
        question_text += ' (В формате [(первое поле,...,последнее поле,),...,(...,)])'
    return question_code, question_text


def sql_preparation(sql_lesson, practical_lesson_result):
    questions = []
    #Вопросы по написанию простого запроса на выдачу данных
    if sql_lesson.write_query:
        questions.append('write')
    #Вопросы по поиску и исправлению ошибки в запросе
    if sql_lesson.error_search:
        questions.append('search')
    #Вопросы по выдаче данных по готовому запросу
    if sql_lesson.result_output:
        questions.append('result')

    cycled_question_list = cycle(questions)

    for i in range(sql_lesson.number_of_questions):
        current = next(cycled_question_list)
        sql_question = CodeQuestion.objects.create(lesson=practical_lesson_result)
        tables = SQLTable.objects.filter(lesson=sql_lesson)
        sql_question.question_code, sql_question.question_text = sql_prepare(tables, current)
        sql_question.answer = run_sql(sql_question.question_code, True)
        sql_question.save()