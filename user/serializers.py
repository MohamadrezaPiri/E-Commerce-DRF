from djoser.serializers import UserCreateSerializer,UserSerializer
from store.models import Customer

class RegisterSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields=['id','username','email','password','first_name','last_name']


class CurrentUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields=['id','username','email','first_name','last_name']

     