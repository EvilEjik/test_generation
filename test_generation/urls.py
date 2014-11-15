from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

from main.views import code_edit


urlpatterns = patterns('',
                       
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^code/', code_edit),
    url(r'^practic/', include('practic.urls')),

    url(r'^accounts/', include('accounts.urls')),

    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
