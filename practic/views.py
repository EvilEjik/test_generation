from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django.http import HttpResponse
import simplejson

from datetime import datetime

from practic.forms import TheoryPracticalLessonForm, TheoryQuestionFormSet, MatrixPracticalLessonForm
from practic.models import *

from main.views import  run_code
from practic.matrix import matrix_preparation


def add_matrix_lesson(request):
    if request.method == 'POST':
        lesson_form = MatrixPracticalLessonForm(request.POST)
        if lesson_form.is_valid():
            lesson = lesson_form.save(commit=False)
            lesson.professor = request.user
            lesson.date = datetime.now()
            lesson.save()
            return HttpResponseRedirect('/practic/success')
    else:
        lesson_form = MatrixPracticalLessonForm()
        return render(request, 'matrix_add.html', {'lesson_form': lesson_form})


def add_theory_lesson(request):
    if request.method == 'POST':
        formset = TheoryQuestionFormSet(request.POST)
        lesson_form = TheoryPracticalLessonForm(request.POST)

        if formset.is_valid() and lesson_form.is_valid():
            lesson = lesson_form.save(commit=False)
            lesson.professor = request.user
            lesson.date = datetime.now()
            lesson.save()

            for form in formset:
                question = form.save(commit=False)
                question.lesson = lesson
                question.save()
            return HttpResponseRedirect('/practic/success')
    else:
        formset = TheoryQuestionFormSet(queryset=TheoryQuestion.objects.none())
        lesson_form = TheoryPracticalLessonForm()
        return render(request, 'theory_add.html', {'formset': formset, 'lesson_form': lesson_form})


class PracticalLessonList(ListView):
    model = PracticalLesson
    context_object_name = 'practical_lessons'


def matrix_solve(request, practical_lesson_id):
    if request.POST:
        answers_list = request.POST.getlist('values[]')

        practical_lesson = get_object_or_404(PracticalLesson, id=practical_lesson_id)
        practical_lesson_result = get_object_or_404(PracticalLessonResult, practical_lesson=practical_lesson)
        questions = MatrixQuestion.objects.filter(lesson=practical_lesson_result)
        practical_lesson_result.max = questions.count()
        practical_lesson_result.date = datetime.now()
        results_dict = dict()

        for (index, answer_text) in enumerate(answers_list):
            next_answer, created = MatrixAnswer.objects.get_or_create(
                question=questions[index], defaults={'answer': answer_text, 'is_true': False, 'result': ""})

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


def practical_lesson_detail(request, practical_lesson_id):
    practical_lesson = get_object_or_404(PracticalLesson, id=practical_lesson_id)
    practical_lesson_result, created = PracticalLessonResult.objects.get_or_create(
        practical_lesson=practical_lesson, student=request.user,
        defaults={'date': datetime.now(), 'result': 0, 'max': 0})
    practical_lesson_result.result = 0
    practical_lesson_result.save()
    if practical_lesson.matrixpracticallesson:
        MatrixQuestion.objects.filter(lesson=practical_lesson_result).delete()
        matrix_lesson = practical_lesson.matrixpracticallesson
        matrix_preparation(matrix_lesson, practical_lesson_result)
        questions = MatrixQuestion.objects.filter(lesson=practical_lesson_result)
        return render(request, 'matrix_solve.html', {'practical_lesson': practical_lesson,
                                          'matrix_lesson': matrix_lesson,
                                          'questions': questions})

    elif practical_lesson.theorypracticallesson:
        print('sdsd')
    else:
        print('sdsd')