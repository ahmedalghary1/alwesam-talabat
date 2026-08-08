from django import forms

from .models import HomeSlide


class HomeSlideForm(forms.ModelForm):
    TARGET_WIDTH = 2048
    TARGET_HEIGHT = 886
    TARGET_RATIO = TARGET_WIDTH / TARGET_HEIGHT
    RATIO_TOLERANCE = 0.01

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

        uploaded_image = self.files.get(self.add_prefix('image'))
        if uploaded_image:
            width, height = uploaded_image.image.size
            ratio = width / height
            if abs(ratio - self.TARGET_RATIO) > self.RATIO_TOLERANCE:
                raise forms.ValidationError(
                    'نسبة الصورة غير مناسبة. استخدم مقاس 2048×886 أو نفس النسبة.'
                )
        return image
