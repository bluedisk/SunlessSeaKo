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

    path('api/like/<str:action>/<str:target_type>/<int:target_id>/', views.like, name='like'),
    path('api/post/<str:entry_id>/', views.add_post, name='add_post'),

    path('', views.home)
]
