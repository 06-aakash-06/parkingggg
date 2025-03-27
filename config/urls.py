from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Smart Parking API",
        default_version='v1',
        description="API for Smart Parking System",
        terms_of_service="https://www.smartparking.com/terms/",
        contact=openapi.Contact(email="contact@smartparking.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Frontend Views
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', include('users.urls_frontend')),
    path('register/', include('users.urls_frontend')),
    
    # App Frontend Views
    path('parking/', include('parking.urls_frontend')),
    path('bookings/', include('parking.urls_frontend')),
    path('profile/', include('users.urls_frontend')),
    path('legal/', include('config.urls_legal')),
    path('wallet/', include('payments.urls_frontend')),
    
    # API Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('users.urls')),
    path('api/parking/', include('parking.urls')),
    path('api/payments/', include('payments.urls')),
    
    # Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)