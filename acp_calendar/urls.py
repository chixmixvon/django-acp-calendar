from django.conf.urls import url, include
from django.views.generic import TemplateView

from .views import CalculatorView, CalendarView

urlpatterns = [
    url(r'^calculator/',  CalculatorView.as_view(), name='calculator'),
    url(r'^fiscal-year-calendar/(?P<fiscal_year>\d{4})',  CalendarView.as_view(), name='fiscal-year-calendar'),
    url(r'^api/', include('acp_calendar.api.urls', namespace='calendar-api')),
    ]
