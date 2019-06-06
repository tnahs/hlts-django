from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core import serializers

from .models import Passage, Source
from .forms import PassageForm


def index(request):
    return render(request, "passages/index.html")


def view(request):

    view_passages = Passage.objects.all()
    all_sources = Source.objects.all()

    passages = []
    for passage in view_passages:
        passages.append({
            "uuid": passage.uuid,
            "passage": passage,
            "form": PassageForm(instance=passage)
        })

    context = {
        "passages": passages,
        "all_sources": all_sources
    }

    return render(request, "passages/view.html", context)


@require_POST
def save(request, uuid):
    """ via. https://docs.djangoproject.com/en/2.2/topics/forms/modelforms/#the-save-method """

    passage = Passage.objects.get(uuid=uuid)

    form = PassageForm(request.POST, instance=passage)

    # print(request.POST)
    # return JsonResponse({
    #     "debug": True,
    # })

    if form.is_valid():
        passage = form.save()
        serialized = serializers.serialize("json", [passage])

        return JsonResponse({
            "success": True,
            "passage": serialized,
        })

    return JsonResponse({
        "success": False,
        "errors": form.errors.as_json(escape_html=True),
    })


def add(request):

    if request.method == "POST":

        form = PassageForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("view")

    else:

        form = PassageForm()

    context = {
        "form": form,
    }

    return render(request, "passages/add.html", context)
