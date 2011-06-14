from django.shortcuts import render
from categories.forms import CategoryForm


def home(request, template_name="home.html"):
    form = CategoryForm(request.POST or None)
    if request.method == "POST":
        print request.POST
    return render(request, template_name, {'form': form})
