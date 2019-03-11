"""sunless_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('admin/', RedirectView.as_view(url="/work/")),
    path('work/', admin.site.urls),

    path('nouns/', views.nouns),
    path('download/<int:patch_id>/', views.download, name='download'),

    path('api/entry/<int:entry_id>/', views.get_entry, name='entry'),
    path('api/like/<str:action>/<str:target_type>/<int:target_id>/', views.like, name='like'),
    path('api/translate/<str:entry_id>/', views.add_translate, name='add_translate'),
    path('api/discuss/<str:translate_id>/', views.add_discuss, name='add_discuss'),
    path('api/translate/delete/<str:trans_id>/', views.del_translate, name='del_translate'),
    path('api/discuss/delete/<str:discuss_id>/', views.del_discuss, name='del_discuss'),

    path('', views.home)
]
