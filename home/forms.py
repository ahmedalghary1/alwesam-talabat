from django import forms

from .models import HomeSlide


class HomeSlideForm(forms.ModelForm):
    class Meta:
        model = HomeSlide
        fields = ['title', 'image', 'alt_text', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'مثال: عروض الوسام',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-input',
                'accept': 'image/jpeg,image/png,image/webp',
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'وصف مختصر لمحتوى الصورة',
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and getattr(image, 'size', 0) > 12 * 1024 * 1024:
            raise forms.ValidationError('حجم الصورة يجب ألا يتجاوز 12 ميجابايت.')
        return image
