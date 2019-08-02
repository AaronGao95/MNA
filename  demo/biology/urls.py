"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from biology import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path(r'', views.home, name='home'),
    url(r'^download/(?P<input_hash_id>.{32})/$(?i)', views.download, name='download'),
    url(r'^ajax_search/$(?i)', views.ajax_search, name="ajax_search"),
    url(r'^download-content/(?P<input_hash_id>.{32})/(?P<save_flag>(txt|csv))/$(?i)',views.download_content, name='download_content'),
    url(r'^decomp/results/(?P<file_id>.{32})$(?i)', views.decomposition, name='decomp_results'),
    # url(r'^decomp/download/result/(?P<input_hash_id>.{32})$(?i)', views.decomp_download, name='decomp_download_result'),
    url(r'^decomp/visualisation/(?P<file_id>.{32})$(?i)', views.visualisation, name='decomp_visualisation'),
    url(r'^decomp/visualisation/download/(?P<img_id>.{34,})$(?i)', views.vis_download, name='visualisation_download'),
    url(r'^decomp/search/(?P<file_id>.{32})$(?i)', views.search, name='search'),
    url(r'^ajax_view/$(?i)', views.ajax_view, name="ajax_view"),
    url(r'^search_download/$(?i)', views.search_download, name="search_download"),
    url(r'^guidance/$(?i)', views.guidance, name="guidance"),
    url(r'^decomp/upload/$(?i)', views.decomp_upload, name="decomp_upload"),
    url(r'^decomp/scripts/$(?i)', views.decomp_scripts, name="decomp_scripts"),
    url(r'^download_scripts/(?P<os>.{1})/$(?i)', views.download_scripts, name='download_scripts'),
    url(r'^ajax_uplaod/$(?i)', views.ajax_upload, name="ajax_upload"),
    url(r'^generate_input/(?P<input_hash_id>.{32})/$(?i)', views.generate_input, name="generate_input"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'views.handler404'
