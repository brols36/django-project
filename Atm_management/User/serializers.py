from rest_framework import serializers
from .models import CustomUser, UserTransaction


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=200, required=True)
    security_deposit = serializers.IntegerField(required=True)  # Renamed field

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'security_deposit', 'is_login', 'is_active', 'open_balance')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            security_deposit=validated_data.get('security_deposit'),
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class UserTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTransaction
        fields = ['user_id', 'deposit_amount', 'withdraw', 'transaction_type']
