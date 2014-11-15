from django.forms import ModelForm
from django.forms.models import modelformset_factory

from practic.models import TheoryPracticalLesson, TheoryQuestion, MatrixPracticalLesson


class TheoryPracticalLessonForm(ModelForm):
    class Meta:
        model = TheoryPracticalLesson
        exclude = ['professor', 'date']


class TheoryQuestionForm(ModelForm):
    class Meta:
        model = TheoryQuestion
        fields = ['object', 'subject', 'is_obligatory']


class MatrixPracticalLessonForm(ModelForm):
    class Meta:
        model = MatrixPracticalLesson
        exclude = ['professor', 'date', 'matrix']

TheoryQuestionFormSet = modelformset_factory(TheoryQuestion, exclude=('lesson',), extra=1)