"""
Serializers for accounts app - User authentication and profiles.
"""
from rest_framework import serializers
from accounts.models import CustomUser, Profile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model."""
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'address', 'is_active', 'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']

    def validate_email(self, value):
        email = (value or '').strip().lower()
        if not email:
            return None
        queryset = CustomUser.objects.filter(email__iexact=email)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('هذا البريد الإلكتروني مستخدم بالفعل.')
        return email


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'image']





class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'address', 
                  'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "كلمات المرور غير متطابقة"
            })
        return attrs

    def validate_email(self, value):
        email = (value or '').strip().lower()
        if not email:
            return None
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('هذا البريد الإلكتروني مستخدم بالفعل.')
        return email
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email') or None,
            phone=validated_data['phone'],
            address=validated_data['address'],
            password=validated_data['password'],
            is_active=False  # Requires admin approval
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login credentials."""
    username = serializers.CharField()  # Can be phone, email, or username
    password = serializers.CharField(write_only=True)
