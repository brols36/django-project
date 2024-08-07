from rest_framework.exceptions import ValidationError

from .models import CustomUser, UserTransaction
from rest_framework.decorators import api_view
from .serializers import UserSerializer, UserTransactionSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.views import APIView
from .utils import generate_access_token, decode_token, SECRET_KEY, token_required


@api_view(['POST'])
def register_user(request):
    """
      Registers a new user. Expects username, email, and password in the request data.
      If valid, creates and returns the user data.
      """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_login(request):
    """
      Logs in a user using either username or email and password.
      If successful, generates and returns an access token.
      """
    username_or_email = request.data.get('username')
    password = request.data.get('password')

    if not username_or_email or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = None
    try:
        user = CustomUser.objects.get(
            Q(username=username_or_email) | Q(email=username_or_email)
        )
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not (user.check_password(password)):
        return Response({'error': 'Incorrect Password'}, status=status.HTTP_400_BAD_REQUEST)

    if user:
        access_token = generate_access_token(user)
        user.is_login = True
        user.is_active = True
        user.token = str(access_token)
        user.save()
        user_data = UserSerializer(user).data
        return Response({'data': {'token': access_token, **user_data}}, status=status.HTTP_200_OK)

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@token_required
def user_logout(request):
    """
       Logs out the user by invalidating the access token.
       """
    try:
        user_id = request.user_id
        user_inst = CustomUser.objects.get(id=user_id)
        user_inst.token = None
        user_inst.save()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@token_required
def deposit(request):
    """
       Allows the user to deposit an amount into their account.
       Validates the deposit amount and updates the balance.
       """
    try:
        user_id = request.user_id
        deposit_amount = request.data.get('deposit_amount')

        try:
            if float(deposit_amount) <= 0:
                return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        user_inst = CustomUser.objects.get(id=user_id)
        current_amount = user_inst.open_balance
        new_open_balance = current_amount + float(deposit_amount)
        user_inst.open_balance = new_open_balance

        # Create a transaction record for the deposit
        transaction = UserTransaction.objects.create(
            user_id=user_inst, 
            deposit_amount=deposit_amount,
            withdraw=0,
            transaction_type="Deposit"
        )
        transaction.save()
        user_inst.save()

        return Response({"message": "Amount deposited successfully"}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@token_required
def withdraw(request):
    """
        Allows the user to withdraw an amount from their account.
        Validates the withdrawal amount and updates the balance.
        """
    try:
        user_id = request.user_id
        withdraw = request.data.get('withdraw')

        try:
            if float(withdraw) <= 0:
                return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        user_inst = CustomUser.objects.get(id=user_id)
        current_amount = user_inst.open_balance
        new_open_balance = current_amount - float(withdraw)
        user_inst.open_balance = new_open_balance

        # Create a transaction record for the withdrawal
        transaction = UserTransaction.objects.create(
            user_id=user_inst,
            deposit_amount=0,
            withdraw=withdraw,
            transaction_type="Withdraw"
        )
        transaction.save()
        user_inst.save()

        return Response({"message": "Withdraw Amount successfully"}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@token_required
def check_balance(request):
    """
     Returns the current balance of the user.
     """
    try:
        user_id = request.user_id
        user_inst = CustomUser.objects.get(id=user_id)
        balance = user_inst.open_balance

        return Response({"balance": balance}, status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@token_required
def transaction_history(request):
    """
      Returns the transaction history for the user along with the total amount.
    """
    try:
        user_id = request.user_id
        user = CustomUser.objects.get(id=user_id)

        transaction_type = request.query_params.get('transaction_type')
        if transaction_type in ['Deposit', 'Withdraw']:
            transactions = UserTransaction.objects.filter(user_id=user_id, transaction_type=transaction_type)
        else:
            transactions = UserTransaction.objects.filter(user_id=user_id)

        transaction_data = UserTransactionSerializer(transactions, many=True).data

        security_deposit = user.security_deposit
        total_deposits = sum(transaction['deposit_amount'] for transaction in transaction_data)
        total_withdrawals = sum(transaction['withdraw'] for transaction in transaction_data)

        total_amount = security_deposit + total_deposits - total_withdrawals

        return Response({
            "username": user.username,
            "transaction": transaction_data,
            "total_amount": total_amount,
            "security_deposit": security_deposit
        }, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
