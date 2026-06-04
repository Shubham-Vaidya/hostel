from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Hostel module — namespaced at /hostel/
    path('hostel/', include('hostel.urls', namespace='hostel')),

    # Root → redirect to /hostel/ (backward compat, clean URL)
    path('', RedirectView.as_view(url='/hostel/', permanent=False)),
]