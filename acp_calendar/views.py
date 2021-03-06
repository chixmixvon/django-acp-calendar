from datetime import date
from django.contrib import messages
from django.shortcuts import render
from django.views.generic import View
from django.utils import timezone

from . import __version__ as current_version
from .exceptions import ACPCalendarException
from .models import ACPHoliday, FiscalYear
from .forms import CalculatorForm

class CalendarView(View):
    """
    View to generate a calendar for fiscal year containg the working days in every month
    of the fiscal year.
    """

    template_name = 'acp_calendar/fiscal_year_calendar.html'

    def get(self, request, *args, **kwargs):
        year = int(kwargs['fiscal_year'])
        fiscal_year = FiscalYear(year)
        data = dict()
        data['months'] = list()
        data['version'] = current_version
        data['fiscal_year'] = year
        data['working_days_in_fiscal_year'] = 0
        try:
            for month in fiscal_year.months_in_fiscal_year():
                month_data = dict()
                month_data['month'] = date(month[1], month[0], 1).strftime('%b')
                month_data['year'] = month[1]
                month_data['working_days'] = ACPHoliday.get_working_days_for_month(month[1], month[0])
                data['working_days_in_fiscal_year'] += month_data['working_days']
                data['months'].append(month_data)
            today = timezone.now().date()
            if today <= fiscal_year.end_date:
                data['remaining_working_days_in_fiscal_year'] = ACPHoliday.get_working_days(today, fiscal_year.end_date)
            else:
                data['remaining_working_days_in_fiscal_year'] = 0

            data['remaining_working_days_percentage'] = data['remaining_working_days_in_fiscal_year'] / data['working_days_in_fiscal_year'] *100
        except ACPCalendarException as e:
            data['errors'] = str(e)
        return render(request, self.template_name, data)


class CalculatorView(View):

    template_name = 'acp_calendar/calculator.html'

    def get(self, request, *args, **kwargs):
        form = CalculatorForm()
        data = {'form': form,
                'version': current_version}
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        calculator_form = CalculatorForm(request.POST)
        data = {'form': calculator_form,
                'working_days': None,
                'version': current_version}
        if calculator_form.is_valid():
            start_date = calculator_form.cleaned_data['start_date']
            end_date = calculator_form.cleaned_data['end_date']
            try:
                working_days = ACPHoliday.get_working_days(start_date, end_date)
                data['working_days'] = working_days
                return render(request, self.template_name, data)
            except ACPCalendarException as e:
                messages.add_message(request, messages.ERROR, str(e), extra_tags='dragonball')
                return render(request, self.template_name, data)
        else:
            return render(request, self.template_name, data)

