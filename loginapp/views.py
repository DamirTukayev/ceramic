from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from .models import Visit
from django.shortcuts import render, redirect
from datetime import datetime, timedelta, date
from .services import check_status, superuser_required, handle_login, show_login_form, show_qr_scan_again, handle_user_login, handle_user_logout, get_filtered_visits, download_visits_report
from django.urls import reverse
from django.core.cache import cache
from django.template import loader
from .forms import UserFilterForm

def base(request):
    return render(request, "loginapp/base.html")

def index(request, secret_key):
    code = cache.get('code')
    if secret_key == str(code):
        if request.method == 'POST':
            return handle_login(request)
        else:
            return show_login_form(request)
    else:
        return show_qr_scan_again(request, code)

def home(request):
    user_id = request.user.id
    username = request.user.username
    user = User.objects.get(id=user_id)
    current_date = date.today()
    todayVisit = Visit.objects.filter(Q(user=user) & Q(date=current_date))
    if todayVisit.exists() == False:
        return handle_user_login(user, username, current_date)
    else:
        return handle_user_logout(todayVisit[0], username)

@user_passes_test(lambda u: u.is_superuser)
def qr(request):
    date = datetime.now().date()
    image = f'{date}.png'
    return render(request, 'loginapp/qr.html', {'image': image})

@superuser_required
def ceramic_admin_view(request):
    form = UserFilterForm(request.GET or None)
    search_query = request.GET.get('search', '')

    # Retrieve the date filter from the request GET parameters
    since_date_filter = request.GET.get('date1', '')
    before_date_filter = request.GET.get('date2', '')
    sort_by = request.GET.get('sort_by', '')

    visits = get_filtered_visits(request, search_query, since_date_filter, before_date_filter, sort_by)

    if request.GET.get('download'):
        return download_visits_report(visits, search_query)

    context = {
        'visits': visits,
        'form': form,
        'search_query': search_query,
        'since_date_filter': since_date_filter,
        'before_date_filter': before_date_filter,
        'sort_by': sort_by
    }
    return render(request, 'loginapp/admin.html', context)






