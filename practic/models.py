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
        return str(self.date)


class MatrixPracticalLesson(PracticalLesson):
    number_of_questions = models.IntegerField("Количество вопросов", default=5)
    matrix_traversal_question = models.BooleanField("Задачи на разные типы обхода матриц с выполнением действий",
                                                    default=True)
    search_value_question = models.BooleanField("Задачи на поиск элемента по значению", default=True)
    interaction_question = models.BooleanField("Задачи на установление соответствия между элементами", default=True)
    sort_question = models.BooleanField("Задачи на сортировку матриц", default=True)
    matrix = models.TextField()


class CodeQuestion(models.Model):
    lesson = models.ForeignKey(PracticalLessonResult)
    question_text = models.CharField(max_length=1000)
    question_code = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question_text


class CodeAnswer(models.Model):
    question = models.ForeignKey(CodeQuestion)
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


class SQLPracticalLesson(PracticalLesson):
    number_of_questions = models.IntegerField("Количество вопросов", default=5)
    write_query = models.BooleanField("Задачи на написание запроса", default=True)
    error_search = models.BooleanField("Задачи на поиск ошибки в запросе", default=True)
    result_output = models.BooleanField("Задачи на выдачу результата по запросу", default=True)


class SQLTable(models.Model):
    lesson = models.ForeignKey(SQLPracticalLesson)
    table_name = models.CharField('Название таблицы', max_length=100)

    def __str__(self):
        return self.table_name


class SQLField(models.Model):
    DATA_TYPE_CHOICES = (('Varchar(255)', 'String'), ('Integer', 'Integer'),
                         ('Boolean', 'Boolean'))

    table = models.ForeignKey(SQLTable)
    field_name = models.CharField(max_length=100)
    data_type = models.CharField(choices=DATA_TYPE_CHOICES, max_length=100, default='Integer')
    is_relative = models.BooleanField(default=False)
    relation = models.CharField(max_length=100)

    def __str__(self):
        return self.field_name