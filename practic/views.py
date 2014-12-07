from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
import simplejson

from datetime import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from practic.forms import TheoryPracticalLessonForm, TheoryPairFormSet, MatrixPracticalLessonForm
from practic.models import *

from main.views import run_code
from practic.matrix import matrix_preparation
from practic.theory import theory_preparation


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
    if request.method == 'POST':
        formset = TheoryPairFormSet(request.POST)
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
        formset = TheoryPairFormSet(queryset=TheoryPair.objects.none())
        lesson_form = TheoryPracticalLessonForm()
        return render(request, 'theory_add.html', {'formset': formset, 'lesson_form': lesson_form})


class PracticalLessonList(ListView):
    model = PracticalLesson
    context_object_name = 'practical_lessons'
    template_name = "practicallesson_list.html"


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

        try:
            matrix_lesson = practical_lesson.matrixpracticallesson
        except MatrixPracticalLesson.DoesNotExist:
            try:
                theory_lesson = practical_lesson.theorypracticallesson
            except TheoryPracticalLesson.DoesNotExist:
                print('sdsd')
            else:
                existed_theory_questions = TheoryQuestion.objects.filter(lesson=practical_lesson_result)
                for question in existed_theory_questions:
                    TheoryQuestionElement.objects.filter(question=question).delete()
                existed_theory_questions.delete()

                #Подготовка тестовых вопросов по теоретическим задачам для пр. занятия
                theory_preparation(theory_lesson, practical_lesson_result)

                questions_answers = {}
                questions = TheoryQuestion.objects.filter(lesson=practical_lesson_result)
                for question in questions:
                    questions_answers[question] = TheoryQuestionElement.objects.filter(question=question)
                self.template_name = 'theory_solve.html'
                #context['theory_lesson'] = theory_lesson
                context['questions_answers'] = questions_answers
                return context

        else:
            MatrixQuestion.objects.filter(lesson=practical_lesson_result).delete()

            #Подготовка тестовых вопросов по матрицам для пр. занятия
            matrix_preparation(matrix_lesson, practical_lesson_result)

            questions = MatrixQuestion.objects.filter(lesson=practical_lesson_result)
            self.template_name = 'matrix_solve.html'
            context['matrix_lesson'] = matrix_lesson
            context['questions'] = questions
            return context


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


def theory_solve(request, practical_lesson_id):
    return render(request, 'practical_lesson_result.html')