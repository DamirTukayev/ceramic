from django.shortcuts import redirect, render

def whatchman_required(view_func):
    def decorator_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_whatchman:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'loginapp/404.html')

    return decorator_func