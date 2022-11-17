from django import forms
from .models import Review_Rating

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review_Rating
        fields = ['subject', 'review', 'rating','image']