from django.forms import ModelForm, CheckboxInput, TextInput
from django.forms.models import modelformset_factory, formset_factory

from practic.models import TheoryPracticalLesson, TheoryPair, MatrixPracticalLesson, \
    SQLPracticalLesson, SQLTable, SQLField


class TheoryPracticalLessonForm(ModelForm):
    class Meta:
        model = TheoryPracticalLesson
        exclude = ['professor', 'date']


class MatrixPracticalLessonForm(ModelForm):
    class Meta:
        model = MatrixPracticalLesson
        exclude = ['professor', 'date', 'matrix']


class SQLPracticalLessonForm(ModelForm):
    class Meta:
        model = SQLPracticalLesson
        exclude = ['professor', 'date']


class SQLTableForm(ModelForm):
    class Meta:
        model = SQLTable
        exclude = ['lesson']


class SQLFieldForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['relation'].required = False
        self.fields['is_relative'].required = False

    class Meta:
        model = SQLField
        exclude = ['table']
        widgets = {
            'is_relative': CheckboxInput(attrs={'onchange': "check(this)"}),
            'relation': TextInput(attrs={'disabled': 'true'})
        }


TheoryPairFormSet = modelformset_factory(TheoryPair, exclude=('lesson',), extra=1)
SQLFieldFormSet = formset_factory(form=SQLFieldForm, extra=1)