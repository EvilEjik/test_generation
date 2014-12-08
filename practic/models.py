from django.db import models
from django.contrib.auth.models import User


class PracticalLesson(models.Model):
    professor = models.ForeignKey(User)
    name = models.CharField("Название занятия", max_length=100)
    description = models.CharField("Описание", max_length=100)
    date = models.DateTimeField()
    threshold = models.IntegerField("Порог прохождения", default=100)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.name


class PracticalLessonResult(models.Model):
    practical_lesson = models.ForeignKey(PracticalLesson)
    student = models.ForeignKey(User)
    result = models.IntegerField()
    max = models.IntegerField(default=0)
    date = models.DateTimeField()

    def __str__(self):
        return self.date


class MatrixPracticalLesson(PracticalLesson):
    DATA_TYPE_CHOICES = (
        ('String', 'String'),
        ('Numeral', 'Numeral'),
    )
    number_of_questions = models.IntegerField("Количество вопросов", default=5)
    data_type = models.CharField("Тип данных", max_length=10, choices=DATA_TYPE_CHOICES, default='String')
    matrix_traversal_question = models.BooleanField("Задачи на разные типы обхода матриц с выполнением действий",
                                                    default=True)
    search_value_question = models.BooleanField("Задачи на поиск элемента по значению", default=True)
    interaction_question = models.BooleanField("Задачи на установление соответствия между элементами", default=True)
    sort_question = models.BooleanField("Задачи на сортировку матриц", default=True)
    matrix = models.TextField()


class MatrixQuestion(models.Model):
    lesson = models.ForeignKey(PracticalLessonResult)
    question_text = models.CharField(max_length=300)
    question_code = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question_text


class MatrixAnswer(models.Model):
    question = models.ForeignKey(MatrixQuestion)
    answer = models.TextField()
    result = models.TextField()
    is_true = models.BooleanField(default=False)


class TheoryPracticalLesson(PracticalLesson):
    choice_question = models.BooleanField("Вопросы с выбором ответа из списка", default=True)
    compliance_question = models.BooleanField("Вопросы на соответствие", default=True)
    open_answer_question = models.BooleanField("Вопросы с открытым ответом", default=True)


class TheoryElement(models.Model):
    object = models.CharField(max_length=300)
    subject = models.CharField(max_length=300)

    class Meta:
        abstract = True


class TheoryPair(TheoryElement):
    lesson = models.ForeignKey(TheoryPracticalLesson)
    is_obligatory = models.BooleanField(default=True)


class TheoryQuestion(models.Model):
    lesson = models.ForeignKey(PracticalLessonResult)
    question_type = models.CharField(max_length=100)

    def __str__(self):
        return self.question_type


class TheoryQuestionElement(TheoryElement):
    question = models.ForeignKey(TheoryQuestion)
    is_fake = models.BooleanField(default=False)

    def __str__(self):
        return self.object


class TheoryAnswer(models.Model):
    question = models.ForeignKey(TheoryQuestion)
    result = models.IntegerField(default=0)
    max = models.IntegerField(default=0)


class TheoryAnswerElement(models.Model):
    answer = models.ForeignKey(TheoryAnswer)
    subject = models.CharField(max_length=300)

    def __str__(self):
        return self.subject