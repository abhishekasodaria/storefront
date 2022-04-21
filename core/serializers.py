from djoser.serializers import (UserCreateSerializer as BaseUserCreateSerializer, \
                                UserSerializer as BaseCurrentUserSerializer)

class UserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')


class UserSerializer(BaseCurrentUserSerializer):

    class Meta(BaseCurrentUserSerializer.Meta):
        fields = ('id', 'username', 'email', 'first_name', 'last_name')