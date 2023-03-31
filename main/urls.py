from django.conf import settings
from django.urls import path
from .views import index, profile, login_view, logout_view
from django.conf.urls.static import static


urlpatterns = [
    path('', index),
    path('profile', profile),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
