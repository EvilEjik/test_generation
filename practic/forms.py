from django.forms import ModelForm
from django.forms.models import modelformset_factory

from practic.models import TheoryPracticalLesson, TheoryPair, MatrixPracticalLesson


class TheoryPracticalLessonForm(ModelForm):
    class Meta:
        model = TheoryPracticalLesson
        exclude = ['professor', 'date']


class TheoryPairForm(ModelForm):
    class Meta:
        model = TheoryPair
        fields = ['object', 'subject', 'is_obligatory']


class MatrixPracticalLessonForm(ModelForm):
    class Meta:
        model = MatrixPracticalLesson
        exclude = ['professor', 'date', 'matrix']

TheoryPairFormSet = modelformset_factory(TheoryPair, exclude=('lesson',), extra=1)