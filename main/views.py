from django.shortcuts import render, redirect

from .models import Passage
from .forms import PassageForm


def index(request):
    return render(request, 'main/index.html')


def view(request):

    passages = Passage.objects.order_by('-created')

    context = {'passages' : passages}

    return render(request, 'main/view.html', context)


def add(request):

    if request.method == 'POST':
        form = PassageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PassageForm()

    context = {'form' : form}

    return render(request, 'main/add.html', context)