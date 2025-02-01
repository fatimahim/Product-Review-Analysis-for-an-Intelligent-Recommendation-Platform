from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 4}),
            'rating': forms.Select(attrs={'class': 'w-full p-2 border rounded'})
        }