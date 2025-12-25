from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(label='كلمة المرور', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'أدخل كلمة المرور'}))
    password2 = forms.CharField(label='تأكيد كلمة المرور', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'أعد إدخال كلمة المرور'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'أدخل اسم المستخدم'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'أدخل بريدك الإلكتروني'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'أدخل رقم هاتفك'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'أدخل عنوانك الكامل'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('كلمتا المرور غير متطابقتين')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'أدخل بريدك الإلكتروني'})
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'أدخل كلمة المرور'})
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'address', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        }
