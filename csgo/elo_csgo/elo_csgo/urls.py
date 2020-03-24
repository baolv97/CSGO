"""elo_csgo URL Configuration

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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from bet.views import home_view, detail, refresh, training_elo, refresh_over, detail1, eloplayer,  listperformance
from bet.views import vpgame, over, egame
from django.contrib.auth.views import LoginView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  path('', home_view, name='home'),
                  path('login/', LoginView.as_view(), name='login'),
                  path('bet/', detail, name='detail'),
                  path('betOver/', detail1, name='detail1'),
                  path('refresh/', refresh, name='refresh'),
                  path('training_elo/', training_elo, name='training_elo'),
                  path('list_player/', eloplayer, name='list_player'),
                  path('list_p/',  listperformance, name='list_p'),
                  path('vpgame/', vpgame, name='vpgame'),
                  path('egame/', egame, name='egame'),
                  path('over/', over, name='over'),
                  # path('pin/', changeodds_pin, name='pin'),
                  path('refresh_over/', refresh_over, name='refresh_over'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)
