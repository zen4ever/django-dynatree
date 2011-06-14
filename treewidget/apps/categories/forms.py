from django import forms
from categories.models import Category
from dynatree.widgets import DynatreeWidget

categories = Category.objects.all()

class CategoryForm(forms.Form):
    name = forms.CharField()
    categories = forms.ModelMultipleChoiceField(
        queryset=categories,
        widget = DynatreeWidget(queryset=categories)
    )
