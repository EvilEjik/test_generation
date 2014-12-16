from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
import simplejson
from django.db import connection

from datetime import datetime
from django.views.generic.edit import CreateView
from practic.forms import TheoryPracticalLessonForm, TheoryPairFormSet, MatrixPracticalLessonForm, \
    SQLPracticalLessonForm, SQLTableForm, SQLFieldFormSet

from practic.models import *

from main.views import run_code, run_sql
from practic.matrix import matrix_preparation
from practic.theory import theory_preparation
from practic.sql import sql_preparation


class PracticalLessonList(ListView):
    model = PracticalLesson
    context_object_name = 'practical_lessons'
    template_name = "practicallesson_list.html"


class MatrixLessonCreate(CreateView):
    form_class = MatrixPracticalLessonForm
    template_name = 'matrix_add.html'
    success_url = '/practic/success/'

    def form_valid(self, form):
        lesson = form.save(commit=False)
        lesson.professor = self.request.user
        lesson.date = datetime.now()
        lesson.save()
        return redirect('/practic/success/')


def add_theory_lesson(request):
    lesson_form = TheoryPracticalLessonForm(request.POST or None)
    if request.method == 'POST':
        formset = TheoryPairFormSet(request.POST)

        if formset.is_valid() and lesson_form.is_valid():
            lesson = lesson_form.save(commit=False)
            lesson.professor = request.user
            lesson.date = datetime.now()
            lesson.save()

            for form in formset:
                question = form.save(commit=False)
                question.lesson = lesson
                question.save()
            return HttpResponseRedirect('/practic/success/')
    else:
        formset = TheoryPairFormSet(queryset=TheoryPair.objects.none())
        return render(request, 'theory_add.html', {'formset': formset,
                                                   'lesson_form': lesson_form})


def add_sql_lesson(request):
    lesson_form = SQLPracticalLessonForm(request.POST or None)
    table_form = SQLTableForm(request.POST or None)
    field_formset = SQLFieldFormSet(request.POST or None)
    if request.method == 'POST':
        if field_formset.is_valid() and lesson_form.is_valid() and lesson_form.is_valid():
            lesson = SQLPracticalLesson.objects.filter(name=lesson_form.cleaned_data['name'])

            if not lesson:
                lesson = lesson_form.save(commit=False)
                lesson.professor = request.user
                lesson.date = datetime.now()
                lesson.save()
            else:
                lesson = lesson[0]

            table = table_form.save(commit=False)
            table.lesson = lesson
            table.save()

            for form in field_formset:
                field = form.save(commit=False)
                field.table = table
                field.save()

            if '_one_more' in request.POST:
                table_form = SQLTableForm()
                field_formset = SQLFieldFormSet()
                return render(request, 'sql_add.html', {'lesson_form': lesson_form,
                                                        'field_formset': field_formset,
                                                        'table_form': table_form})

            elif '_finish' in request.POST:
                for table in SQLTable.objects.filter(lesson=lesson):
                    query = ''
                    query += 'CREATE TABLE ' + table.table_name + ' ('
                    for field in SQLField.objects.filter(table=table):
                        query += ' ' + field.field_name + ' ' + field.data_type + ', '
                    query = query[0:-2]
                    query += ' );'
                    cursor = connection.cursor()
                    cursor.execute(query)
                return HttpResponseRedirect('/practic/sql/add_data/')
    else:
        return render(request, 'sql_add.html', {'lesson_form': lesson_form,
                                                'field_formset': field_formset,
                                                'table_form': table_form})


def sql_add_data(request):
    if request.method == 'POST':
        cursor = connection.cursor()
        cursor.execute(request.POST['code_text'])
        return HttpResponse(simplejson.dumps('/practic/success/'), content_type="application/json")
    else:
        return render(request, 'sql_data_add.html')


class PracticalLessonDetail(DetailView):
    model = PracticalLesson
    context_object_name = 'practical_lesson'

    def get_context_data(self, **kwargs):
        practical_lesson = super(PracticalLessonDetail, self).get_object()
        context = super(PracticalLessonDetail, self).get_context_data(**kwargs)
        practical_lesson_result, created = PracticalLessonResult.objects.get_or_create(
            practical_lesson=practical_lesson, student=self.request.user,
            defaults={'date': datetime.now(), 'result': 0, 'max': 0})
        practical_lesson_result.result = 0
        practical_lesson_result.save()

        #Определяем тип практического занятия
        try:
            theory_lesson = practical_lesson.theorypracticallesson
        except TheoryPracticalLesson.DoesNotExist:
            CodeQuestion.objects.filter(lesson=practical_lesson_result).delete()

            try:
                matrix_lesson = practical_lesson.matrixpracticallesson
            except MatrixPracticalLesson.DoesNotExist:
                #Подготовка тестовых вопросов по таблицам для практического занятия
                sql_preparation(practical_lesson.sqlpracticallesson, practical_lesson_result)
                self.template_name = 'sql_solve.html'
                tables_fields = {}
                tables = SQLTable.objects.filter(lesson=practical_lesson.sqlpracticallesson)
                for table in tables:
                    cursor = connection.cursor()
                    cursor.execute("SELECT * FROM " + table.table_name + ';')
                    tables_fields[table.table_name] = [SQLField.objects.filter(table=table), cursor.fetchall()]
                context['tables_fields'] = tables_fields
            else:
                #Подготовка тестовых вопросов по матрицам для практического занятия
                matrix_preparation(matrix_lesson, practical_lesson_result)
                self.template_name = 'matrix_solve.html'
                context['matrix_lesson'] = matrix_lesson

            questions = CodeQuestion.objects.filter(lesson=practical_lesson_result)
            context['questions'] = questions

        else:
            existed_theory_questions = TheoryQuestion.objects.filter(lesson=practical_lesson_result)
            for question in existed_theory_questions:
                TheoryQuestionElement.objects.filter(question=question).delete()
            existed_theory_questions.delete()

            #Подготовка тестовых вопросов по теоретическим задачам для практического занятия
            theory_preparation(theory_lesson, practical_lesson_result)

            questions_answers = {}
            questions = TheoryQuestion.objects.filter(lesson=practical_lesson_result)
            for question in questions:
                questions_answers[question] = TheoryQuestionElement.objects.filter(question=question)
            self.template_name = 'theory_solve.html'
            context['questions_answers'] = questions_answers
        return context


def code_solve(request, practical_lesson_id):
    if request.POST:
        answers_list = request.POST.getlist('values[]')

        practical_lesson = get_object_or_404(PracticalLesson, id=practical_lesson_id)
        practical_lesson_result = get_object_or_404(PracticalLessonResult, practical_lesson=practical_lesson)
        questions = CodeQuestion.objects.filter(lesson=practical_lesson_result)
        practical_lesson_result.max = questions.count()
        practical_lesson_result.date = datetime.now()
        results_dict = dict()

        for (index, answer_text) in enumerate(answers_list):
            next_answer, created = CodeAnswer.objects.get_or_create(
                question=questions[index], defaults={'answer': answer_text, 'is_true': False, 'result': ""})

            try:
                matrix_lesson = practical_lesson.matrixpracticallesson
            except MatrixPracticalLesson.DoesNotExist:
                if questions[index].question_text[:2] == 'По':
                    next_answer.result = answer_text
                else:
                    next_answer.result = run_sql(answer_text, True)
                if str(next_answer.result) == questions[index].answer:
                    next_answer.is_true = True
                    practical_lesson_result.result += 1
                    next_answer.save()
                    results_dict[index] = [next_answer.result, questions[index].answer, next_answer.is_true]
            else:
                file_name = request.COOKIES['csrftoken'] + '.py'
                output, err = run_code(file_name, answer_text)
                if output:
                    next_answer.result = (output.decode()).rstrip()
                else:
                    next_answer.result = err
                if next_answer.result == questions[index].answer.rstrip():
                    next_answer.is_true = True
                    practical_lesson_result.result += 1
                next_answer.save()
                results_dict[index] = [next_answer.result, questions[index].answer, next_answer.is_true]

        practical_lesson_result.save()

        response_data = dict()
        response_data['result'] = practical_lesson_result.result
        response_data['max'] = practical_lesson_result.max
        response_data['results_dict'] = results_dict

        return HttpResponse(simplejson.dumps(response_data), content_type="application/json")


def theory_solve(request, practical_lesson_id):
    if request.POST:
        practical_lesson = get_object_or_404(PracticalLesson, id=practical_lesson_id)
        practical_lesson_result = get_object_or_404(PracticalLessonResult, practical_lesson=practical_lesson)
        questions = TheoryQuestion.objects.filter(lesson=practical_lesson_result)
        practical_lesson_result.date = datetime.now()

        for question in questions:
            question_elements = TheoryQuestionElement.objects.filter(question=question, is_fake=False)
            next_answer = TheoryAnswer.objects.create(question=question)

            if question.question_type == 'open_answer':
                next_element = TheoryAnswerElement.objects.create(answer=next_answer)
                next_element.subject = request.POST.get(str(question.id))
                next_element.save()
                next_answer.max = 3

                if question_elements[0].object.lower() == next_element.subject.lower():
                    next_answer.result = 3

            elif question.question_type == 'compliance':
                next_answer.max = 3
                for element in question_elements:
                    next_element = TheoryAnswerElement.objects.create(answer=next_answer)
                    next_element.subject = request.POST.get(str(element.id))
                    next_element.save()

                    if element.subject.lower() == next_element.subject.lower():
                        next_answer.result += 1

            elif question.question_type == 'choice':
                next_element = TheoryAnswerElement.objects.create(answer=next_answer)
                current_choice = request.POST.get(str(question.id))
                if current_choice:
                    next_element.subject = get_object_or_404(TheoryQuestionElement, id=current_choice).subject
                else:
                    next_element.subject = ''
                next_element.save()
                next_answer.max = 2

                if question_elements[0].subject == next_element.subject:
                    next_answer.result = 2

            next_answer.save()

        result = get_list_or_404(TheoryAnswer, question__in=questions)
        practical_lesson_result.result = sum(r.result for r in result)
        practical_lesson_result.max = sum(r.max for r in result)

        practical_lesson_result.save()
        return HttpResponseRedirect('/accounts/%s/%i/' % (str(request.user.username), practical_lesson_result.id))