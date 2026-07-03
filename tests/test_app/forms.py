from django import forms
from test_app.models import Widget


class WidgetForm(forms.ModelForm):
    class Meta:
        model = Widget
        fields = ["name", "description"]


class CleanErrorForm(forms.Form):
    """A form whose clean() always fails, to exercise __all__ errors."""

    name = forms.CharField(required=False)

    def clean(self):
        raise forms.ValidationError("top level problem")
