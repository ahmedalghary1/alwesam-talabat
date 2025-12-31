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
    
    image = forms.ImageField(label='صورة الملف الشخصي', required=False, widget=forms.FileInput(attrs={'class': 'form-input'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("اسم المستخدم هذا مستخدم بالفعل")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("البريد الإلكتروني هذا مستخدم بالفعل")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("رقم الهاتف هذا مستخدم بالفعل")
        return phone

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

    def save_profile_image(self, user):
        """Save the profile image if provided"""
        image = self.cleaned_data.get('image')
        if image and hasattr(user, 'profile'):
            user.profile.image = image
            user.profile.save()


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
        fields = ['username', 'email', 'phone', 'address']
        labels = {
            'username': 'اسم المستخدم',
            'email': 'البريد الإلكتروني',
            'phone': 'رقم الهاتف',
            'address': 'العنوان',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'أدخل اسم المستخدم'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'أدخل بريدك الإلكتروني'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'أدخل رقم هاتفك'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'أدخل عنوانك الكامل'
            }),
        }
    
    def clean_username(self):
        """التحقق من أن اسم المستخدم فريد"""
        username = self.cleaned_data.get('username')
        if username:
            # التحقق من وجود اسم مستخدم مطابق لمستخدم آخر
            existing_user = CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError('اسم المستخدم هذا مستخدم بالفعل. الرجاء اختيار اسم آخر.')
        return username
    
    def clean_email(self):
        """التحقق من أن البريد الإلكتروني فريد"""
        email = self.cleaned_data.get('email')
        if email:
            # التحقق من وجود بريد إلكتروني مطابق لمستخدم آخر
            existing_user = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError('هذا البريد الإلكتروني مستخدم بالفعل. الرجاء استخدام بريد آخر.')
        return email
    
    def clean_phone(self):
        """التحقق من صحة رقم الهاتف"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # إزالة المسافات والرموز غير الضرورية
            phone = phone.strip()
            if len(phone) < 10:
                raise forms.ValidationError('رقم الهاتف يجب أن يكون 10 أرقام على الأقل.')
        return phone
        if phone:
            # إزالة المسافات والرموز غير الضرورية
            phone = phone.strip()
            if len(phone) < 10:
                raise forms.ValidationError('رقم الهاتف يجب أن يكون 10 أرقام على الأقل.')
        return phone


class ProfileImageForm(forms.ModelForm):
    class Meta:
        from .models import Profile
        model = Profile
        fields = ['image', 'bio']
        labels = {
            'image': 'صورة الملف الشخصي',
            'bio': 'نبذة شخصية',
        }
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'اكتب نبذة عنك...'}),
        }
