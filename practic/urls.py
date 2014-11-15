from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

from practic.views import add_theory_lesson, add_matrix_lesson, PracticalLessonList, practical_lesson_detail, matrix_solve


urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="practic_index.html")),
    url(r'^matrix/$', add_matrix_lesson),
    url(r'^theory/$', add_theory_lesson),
    url(r'^success/', TemplateView.as_view(template_name="add_success.html")),
    url(r'^solve/$', PracticalLessonList.as_view(template_name="practicallesson_list.html")),
    url(r'^solve/(?P<practical_lesson_id>\d+)/$', practical_lesson_detail, name='practical_lesson_detail'),
    url(r'^matrix_solve/(?P<practical_lesson_id>\d+)/$', matrix_solve),
)
