from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FriendRelation
from django.contrib.auth import password_validation


#say whetre to take user model to do not write path everytime when it changes
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    #never returns passwortdfor reading:
    password = serializers.CharField(write_only=True)
    nickname = serializers.CharField(max_length=15)
    class Meta:
        model = User
        fields = ['email', 'password', 'nickname']

    def validate_nickname(self, value):
            if User.objects.filter(nickname=value).exists():
                raise serializers.ValidationError("This nickname is already taken") #catch of exception 09/07/20226 bug fix
            return value

    def validate_password(self, value):
            password_validation.validate_password(value)
            return value

    
    #validated_data - set of data after is_valid() of DRF
    #self same as this in c++
    #create - needs to override default create (from save()) to hash password
    #create_user() - Djangos User manager method that hashes password before saving
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nickname=validated_data['nickname'],
        )
        return user

class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['avatar']
#ImageFiled already knows how to validate (by Pillow librarury for images)


class FriendUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'is_online', 'avatar', 'wins', 'losses']

class FriendRelationSerializer(serializers.ModelSerializer):
    #data takes from method, not directl;y from model
    friend = serializers.SerializerMethodField() #needs to define "from user" or "to_user"

    def get_friend(self, obj): #obj - actual obj from FriendRelation model
        request = self.context['request'] #define user who makes request
        if obj.from_user == request.user: #if  rerquest was send by me
            return FriendUserSerializer(obj.to_user).data  #i sent request to friend (frined - to_user)
        return FriendUserSerializer(obj.from_user).data #else - request cames from friend (friend - from_yser)

    class Meta:
        model = FriendRelation
        fields = ['id', 'status', 'friend']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(max_length=15, required=False)

    class Meta:
            model = User
            fields = ['nickname', 'email']
            extra_kwargs = {
                'email': {'required': False},
            }
    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("This nickname is already taken")
        return value

    