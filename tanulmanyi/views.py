from django.shortcuts import render, redirect
from django.contrib import auth


def home(request):
    return render(request, 'tanulmanyi/home.html')


def login(request):
    return render(request, 'tanulmanyi/login.html')


def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return redirect('/accounts/loggedin')
    else:
        return redirect('/accounts/invalid')


def loggedin(request):
    return render(request, 'tanulmanyi/loggedin.html',
                  {'username': request.user.username})


def invalid_login(request):
    return render(request, 'tanulmanyi/invalid_login.html')


def logout(request):
    auth.logout(request)
    return render(request, 'tanulmanyi/logout.html')