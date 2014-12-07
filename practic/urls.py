from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

from practic.views import add_theory_lesson, PracticalLessonList, matrix_solve, theory_solve, \
    MatrixLessonCreate, PracticalLessonDetail


urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="practic_index.html")),
    url(r'^matrix/$', MatrixLessonCreate.as_view()),
    url(r'^theory/$', add_theory_lesson),
    url(r'^success/', TemplateView.as_view(template_name="add_success.html")),
    url(r'^solve/$', PracticalLessonList.as_view()),
    url(r'^solve/(?P<pk>\d+)/$', PracticalLessonDetail.as_view(), name='practical_lesson_detail'),
    url(r'^matrix_solve/(?P<practical_lesson_id>\d+)/$', matrix_solve),
    url(r'^theory_solve/(?P<practical_lesson_id>\d+)/$', theory_solve, name='theory_solve'),
)
