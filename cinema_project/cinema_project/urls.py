from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Импортируем наш View регистрации
from cinema.views import SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Встроенные маршруты авторизации (login, logout, password_reset...)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # 2. Наш маршрут для регистрации
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    
    # 3. Приложение cinema
    path('', include('cinema.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)