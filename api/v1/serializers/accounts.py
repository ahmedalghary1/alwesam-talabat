"""
Serializers for accounts app - User authentication and profiles.
"""
from rest_framework import serializers
from accounts.models import CustomUser, Profile, Address


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model."""
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'address', 'is_active', 'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'image']


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for user addresses."""
    
    class Meta:
        model = Address
        fields = ['id', 'label', 'street', 'city', 'state', 
                  'postal_code', 'country', 'is_default']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
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
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            address=validated_data['address'],
            password=validated_data['password'],
            is_active=False  # Requires admin approval
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login credentials."""
    username = serializers.CharField()  # Can be email or phone
    password = serializers.CharField(write_only=True)
