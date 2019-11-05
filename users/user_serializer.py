from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.utils import model_meta
from django.contrib.auth.hashers import make_password
from users.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    # email = serializers.CharField(required=False)

    # def validate(self, attrs):
    #     if attrs['password'] != attrs['confirm_password']:
    #         raise serializers.ValidationError({"password": "Did not match"})
    #     if len(attrs['password']) < 8:
    #         raise serializers.ValidationError({"password": ["Password must be at least 8 characters", "sdfsdf"]})
    #     return attrs

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'confirm_password')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = UserProfile
        fields = ('uid', 'user', 'phone_number', 'dob', 'current_organization')

    def create(self, validated_data):
        print("----serial-----")
        print(validated_data)
        print("---------")
        user_data = validated_data.get('user', {})
        if UserProfile.objects.filter(user__username=user_data['username'], user__email=user_data['email']).exists():
            raise serializers.ValidationError({"username": "Username already exist", "email": "Email already exist"})
        elif UserProfile.objects.filter(user__username=user_data['username']).exists():
            raise serializers.ValidationError({"username": "Username already exist"})
        elif UserProfile.objects.filter(user__email=user_data['email']).exists():
            raise serializers.ValidationError({"email": "Email already exist"})
        password = user_data['password']
        confirm_password = user_data.pop('confirm_password', '')
        if password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords did not match"})
        user_data['password'] = make_password(password=password)
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        user_profile = UserProfile.objects.create(user=user, dob=validated_data.get('dob'),
                                                  phone_number=validated_data.get('phone_number'))
        return user_profile

    def update(self, instance, validated_data):
        # method: PUT & PATCH both
        # manually update relational user data
        user_data = validated_data.pop('user', {})
        password = user_data.get('password', '')
        if len(password) > 0:
            confirm_password = user_data.pop('confirm_password', '')
            if password != confirm_password:
                raise serializers.ValidationError("Confirm password didn't match.")
            user_data['password'] = make_password(password)
        UserSerializer.update(UserSerializer(), instance.user, user_data)
        # manual update ends

        serializers.raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        return instance
