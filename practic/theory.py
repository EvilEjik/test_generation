from itertools import cycle
from random import shuffle, sample

from practic.models import TheoryQuestion, TheoryPair, TheoryQuestionElement


def create_question_element(current_pair_element, theory_question, is_fake=False):
    question_element = TheoryQuestionElement.objects.create(question=theory_question)
    question_element.object = current_pair_element.object
    question_element.subject = current_pair_element.subject
    question_element.is_fake = is_fake
    question_element.save()


def theory_preparation(theory_lesson, practical_lesson_result):

    questions = []
    if theory_lesson.choice_question:
        questions.append('choice')
    if theory_lesson.compliance_question:
        questions.append('compliance')
    if theory_lesson.open_answer_question:
        questions.append('open_answer')

    cycled_question_list = cycle(questions)
    theory_pairs = list(TheoryPair.objects.filter(lesson=theory_lesson))
    original_theory_pairs = theory_pairs[:]
    shuffle(theory_pairs)

    while theory_pairs:
        current = next(cycled_question_list)
        theory_question = TheoryQuestion.objects.create(lesson=practical_lesson_result)

        if current == 'choice':
            theory_question.question_type = 'choice'
            theory_question.save()
            if len(original_theory_pairs) < 4:
                theory_question.delete()
                continue
            else:
                current_pair_element = theory_pairs.pop(0)
                create_question_element(current_pair_element, theory_question)
                fake_answers = sample(original_theory_pairs, 3)
                while current_pair_element in fake_answers:
                    fake_answers = sample(original_theory_pairs, 3)

                for fake_answer in fake_answers:
                    create_question_element(fake_answer, theory_question, True)

        elif current == 'compliance':
            if len(theory_pairs) < 3:
                theory_question.delete()
                continue
            else:
                theory_question.question_type = 'compliance'
                theory_question.save()
                for i in range(3):
                    current_pair_element = theory_pairs.pop(0)
                    create_question_element(current_pair_element, theory_question)

        elif current == 'open_answer':
            theory_question.question_type = 'open_answer'
            theory_question.save()
            current_pair_element = theory_pairs.pop(0)
            create_question_element(current_pair_element, theory_question)