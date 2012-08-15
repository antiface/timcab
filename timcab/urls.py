from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'timcab.views.home', name='home'),
    # url(r'^timcab/', include('timcab.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	url(r'vocab/$', 'vocab.views.index'),
	url(r'vocab/review/(?P<studyunit_id>\d+)/$', 'vocab.views.review'),
	url(r'vocab/review/(?P<studyunit_id>\d+)/showback/$', 'vocab.views.showback'),
	url(r'vocab/login/$', 'django.contrib.auth.views.login', {'template_name': 'vocab/login.html'}), 
	url(r'vocab/logout/$', 'django.contrib.auth.views.logout'),
)
