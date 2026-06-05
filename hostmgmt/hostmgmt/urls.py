from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('hostel/', include('hostel.urls', namespace='hostel')),

    path(
        '',
        RedirectView.as_view(
            url='/hostel/dashboard/',
            permanent=False
        )
    ),
]