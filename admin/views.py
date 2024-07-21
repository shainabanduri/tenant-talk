from django.shortcuts import render

# Create your views here.


def adminhome(request):
    return render(request, 'admin/adminhome.html')


def adminaccount(request):
    return render(request, 'admin/adminaccount.html')


