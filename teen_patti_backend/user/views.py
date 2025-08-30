from django.shortcuts import render
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import *
from .models import UserAccount
from django.utils.crypto import get_random_string
from .mail import *
from django.http import JsonResponse
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from .authentication import *
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from djoser.social.views import ProviderAuthView
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from django.contrib.sessions.models import Session
from django.utils.timezone import now
from game.models import UserWallet
from django.db import transaction
from game.models import UserWallet
from .utils import *
from decimal import Decimal, InvalidOperation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# from candidateapp.models import FCMToken

logger = logging.getLogger(__name__)


# class RegisterView(APIView):
#     """
#     A view for registering new admin users.

#     This view supports POST method.

#     POST:
#     Registers a new admin user with a randomly generated code and the role set to 'admin'.
#     Upon successful registration, a verification code is sent to the user's email for confirmation.

#     Parameters:
#     - request_data: The request data containing user information.
    
#     Returns:
#     - 201 Created if the user is successfully created.
#     - 500 Internal Server Error if an unexpected error occurs during processing.

#     Explanation:
#     1. Generate a random code for the user.
#     2. Set the user's role to 'admin'.
#     3. Validate the request data using the AdminSignupSerializer.
#     4. Save the serialized data to create the user.
#     5. Send the verification code to the user's email for confirmation.

#     Note: Detailed error handling is implemented to handle unexpected errors.
#     """
#     authentication_classes = []
#     @swagger_auto_schema(
#         operation_description="Register a new user with optional referral code.",
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             required=["email", "role"],
#             properties={
#                 'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
#                 'role': openapi.Schema(type=openapi.TYPE_STRING, description="User role (admin/player)"),
#                 'referral_code': openapi.Schema(type=openapi.TYPE_STRING, description="Optional referral code"),
#             },
#         ),
#         responses={201: "User Created Successfully", 400: "Bad Request"}
#     )
#     # def post(self, request):
#     #     try:
#     #         request_data = request.data
#     #         email = request.data['email']
#     #         if UserAccount.objects.filter(email=email).exists() or \
#     #             UserAccount.objects.filter(email_changed__contains=[{'old_email': email}]).exists():
#     #                 return Response({'error': 'The new email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)
#     #         request_data['code'] = generate_random_otp()
#     #         request_data['role'] = request.data['role']
#     #         serializer = RegisterSerializer(data=request_data)
#     #         serializer.is_valid(raise_exception=True)
#     #         serializer.save()
#     #         sent_to = serializer.data['email']
#     #         message = serializer.data['code']
#     #         print(sent_to)
#     #         codeverify(sent_to,message)
#     #         return Response({'Response':'User Created Successfully'} , status=status.HTTP_201_CREATED)
#     #     except KeyError as e:
#     #         return Response({'error': f'Missing key: {e}'}, status=status.HTTP_400_BAD_REQUEST)
#     #     except Exception as e:
#     #         return Response({'error': f'{e} Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#     def post(self, request):
#         try:
#             request_data = request.data
#             email = request_data['email']
#             referral_code = request_data.get('referral_code')

#             if UserAccount.objects.filter(email=email).exists() or \
#                 UserAccount.objects.filter(email_changed__contains=[{'old_email': email}]).exists():
#                 return Response({'error': 'The email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)

#             request_data['code'] = generate_random_otp()
#             request_data['role'] = request_data['role']

#             if referral_code:
#                 try:
#                     print('hsdbfkbshk',referral_code)
#                     referred_by = UserAccount.objects.get(referral_code=referral_code)
#                     print('referral_code',referred_by.id)
#                     if referred_by.verify:
#                         request_data['referred_by'] = referred_by.id
#                     else:
#                         return Response({'error': 'Referral code is not verified.'}, status=status.HTTP_400_BAD_REQUEST)
#                     request_data['referred_by'] = referred_by.id
#                 except UserAccount.DoesNotExist:
#                     return Response({'error': 'Invalid referral code.'}, status=status.HTTP_400_BAD_REQUEST)

#             serializer = RegisterSerializer(data=request_data)
#             serializer.is_valid(raise_exception=True)
#             user = serializer.save()

#             codeverify(user.email, user.code)

#             return Response({
#                 'response': 'User Created Successfully',
#                 'referral_code': user.referral_code
#             }, status=status.HTTP_201_CREATED)

#         except KeyError as e:
#             return Response({'error': f'Missing key: {e}'}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'error': f'{e} Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterView(APIView):
    """
    A view for registering new admin users.

    This view supports POST method.

    POST:
    Registers a new admin user with a randomly generated code and the role set to 'admin'.
    Upon successful registration, a verification code is sent to the user's email for confirmation.

    Parameters:
    - request_data: The request data containing user information.
    
    Returns:
    - 201 Created if the user is successfully created.
    - 500 Internal Server Error if an unexpected error occurs during processing.
    """
    authentication_classes = []
    @swagger_auto_schema(
        operation_description="Register a new user with optional referral code.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "role", "username", "mobile", "password", "otp"],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description="User name"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                'mobile': openapi.Schema(type=openapi.TYPE_STRING, description="User mobile number"),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description="One Time Password"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="User password"),
                'role': openapi.Schema(type=openapi.TYPE_STRING, description="User role (admin/player)"),
                'referral_code': openapi.Schema(type=openapi.TYPE_STRING, description="Optional referral code"),
            },
        ),
        responses={201: "User Created Successfully", 400: "Bad Request"}
    )
    def post(self, request):
        try:
            request_data = request.data
            email = request_data['email']
            referral_code = request_data.get('referral_code')

            # Check for duplicate email
            if UserAccount.objects.filter(email=email).exists() or \
                UserAccount.objects.filter(email_changed__contains=[{'old_email': email}]).exists():
                return Response({'error': 'The email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)

            # Add generated code and role
            request_data['code'] = "123456"
            request_data['role'] = request_data['role']

            # Handle referral code if provided
            if referral_code:
                try:
                    referred_by = UserAccount.objects.get(referral_code=referral_code)
                    if referred_by.verify:
                        request_data['referred_by'] = referred_by.id
                    else:
                        return Response({'error': 'Referral code is not verified.'}, status=status.HTTP_400_BAD_REQUEST)
                except UserAccount.DoesNotExist:
                    return Response({'error': 'Invalid referral code.'}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize and save
            serializer = RegisterSerializer(data=request_data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # Send verification code
            codeverify(user.email, user.code)

            return Response({
                'response': 'User Created Successfully',
                'referral_code': user.referral_code,
                'code': "123456"
            }, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response({'error': f'Missing key: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'{e} Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





# verify user details
class Verify(APIView):
    """
    A view for verifying user details.

    This view supports POST method.

    POST:
    Verifies user details based on the provided verification code and email address.
    If the code matches the one stored in the database for the given email, the user is marked as verified.

    Parameters:
    - code (str): The verification code sent to the user.
    - email (str): The email address of the user to be verified.

    Returns:
    - 200 OK with the verification status ('True' if verified, 'False' if not) if verification is successful.
    - 403 Forbidden if the provided code does not match the one stored in the database.
    - 404 Not Found if the provided email does not exist in the database.
    - 400 Bad Request if the request data is invalid or incomplete.
    - 500 Internal Server Error if an unexpected error occurs during processing.
    """
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Verify user with code and email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["code", "email"],
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description="Verification code"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
            },
        ),
        responses={200: "Verified", 403: "Code mismatch", 404: "Email not found"}
    )
    
    # def post(self, request):
    #     try:
    #         code = request.data['code']
    #         email = request.data['email']
            
    #         if UserAccount.objects.filter(email=email).exists():
    #             verify_code = UserAccount.objects.filter(email=email).values_list('code')[0][0]
                
    #             if verify_code == code:
    #                 UserAccount.objects.filter(email=email).update(verify=True)
    #                 verify = UserAccount.objects.filter(email=email).values_list('verify')[0][0]
    #                 return Response(verify, status=status.HTTP_200_OK)
    #             else:
    #                 return Response({'response''Code mismatch'}, status=status.HTTP_403_FORBIDDEN)
    #         else:
    #             return Response({'response':'This email does not exist'}, status=status.HTTP_404_NOT_FOUND)
    #     except KeyError:
    #         return Response({'response':'Invalid request data. Please provide both code and email.'}, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({'status':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def post(self, request):
        try:
            code = request.data.get('code')
            email = request.data.get('email')

            if not code or not email:
                return Response({'response': 'Invalid request data. Please provide both code and email.'}, status=status.HTTP_400_BAD_REQUEST)

            user = UserAccount.objects.filter(email=email).first()

            if not user:
                return Response({'response': 'This email does not exist'}, status=status.HTTP_404_NOT_FOUND)

            if user.code != code:
                return Response({'response': 'Code mismatch'}, status=status.HTTP_403_FORBIDDEN)

            with transaction.atomic():
                user.verify = True
                user.save()

                wallet, created = UserWallet.objects.get_or_create(user=user, defaults={'balance': 100.00})

                # if user.referred_by:
                #     wallet.balance += 100
                #     wallet.save()
            return Response({'verified': True, 'wallet_created': created}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReferralLinkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get referral link for the authenticated user",
        responses={
            200: openapi.Response(
                description="Referral link retrieved successfully",
                examples={
                    "application/json": {
                        "referral_code": "ABC123",
                        "referral_link": "https://teenpatti.com/register?ref=ABC123"
                    }
                }
            ),
            404: openapi.Response(
                description="Referral code not found",
                examples={
                    "application/json": {"error": "Referral code not found for user."}
                }
            ),
            500: openapi.Response(
                description="Server error",
                examples={
                    "application/json": {"error": "Some error message"}
                }
            ),
        }
    )

    def get(self, request):
        try:
            user = request.user

            if not user.referral_code:
                return Response({'error': 'Referral code not found for user.'}, status=status.HTTP_404_NOT_FOUND)

            referral_link = f"https://teenpatti.com/register?ref={user.referral_code}"

            return Response({
                "referral_code": user.referral_code,
                "referral_link": referral_link
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RetrieveUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve current authenticated user",
        operation_description="Returns the authenticated user's profile details.",
        responses={200: UserSerializer}
    )

    def get(self, request):
        try:
            user = request.user
            print(user)
            user = UserSerializer(user)

            return Response(user.data, status=status.HTTP_200_OK)
        except Exception as e:
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Update current authenticated user",
        operation_description="Partially update the authenticated user's profile.",
        request_body=UserSerializer,
        responses={200: UserSerializer}
    )

    def patch(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


  
  

class RevokeAccessTokenView(APIView):
   authentication_classes = [CustomJWTAuthentication]
   permission_classes = [permissions.IsAuthenticated]

   @swagger_auto_schema(
        operation_summary="Revoke current access token",
        operation_description="Revokes (blacklists) the currently authenticated access token.",
        responses={
            200: openapi.Response(
                description="Token successfully blacklisted",
                examples={
                    "application/json": {
                        "message": "Access token blacklisted"
                    }
                }
            ),
            500: openapi.Response(
                description="Server error",
                examples={
                    "application/json": {
                        "message": "Error Raised some error message"
                    }
                }
            )
        }
    )


   def post(self, request):
      try:
        access_token = request.META.get('HTTP_AUTHORIZATION', '').split('Bearer ')[-1]
        RevokedToken.objects.create(token=access_token)
        return Response({'message': 'Access token blacklisted'}, status=status.HTTP_200_OK)
      except Exception as e:
        return Response({'message': f'Error Raised {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





# resend email
class EmailResendView(APIView):
    """
        A view for resending verification emails to admin users.

        This view allows sending a verification email to an admin user if they haven't been verified yet.

        Methods:
            post(self, request): Handles POST requests to resend verification emails.
                Args:
                    request (Request): The HTTP request object containing the email address.
                Returns:
                    Response: JSON response indicating the status of the email resend operation.
                        If successful, returns status code 200 with a success message.
                        If the email address is missing, returns status code 400 with an error message.
                        If the user with the provided email address is not found or is not an admin, returns status code 404 with an error message.
                        If the user is already verified, returns status code 400 with an error message.
                        If any other error occurs, returns status code 500 with an error message.
        """
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Resend verification email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
            },
        ),
        responses={200: "Email resent", 400: "Invalid", 404: "User not found"}
    )

    def post(self, request):
        """
        Handles POST requests to resend verification emails.

        Args:
            request (Request): The HTTP request object containing the email address.

        Returns:
            Response: JSON response indicating the status of the email resend operation.
                If successful, returns status code 200 with a success message.
                If the email address is missing, returns status code 400 with an error message.
                If the user with the provided email address is not found or is not an admin, returns status code 404 with an error message.
                If the user is already verified, returns status code 400 with an error message.
                If any other error occurs, returns status code 500 with an error message.
        """

        email = request.data.get('email', None)

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserAccount.objects.get(email=email, role='admin')
        except UserAccount.DoesNotExist:
            return Response({'error': 'User with this email not found or is not a company'}, status=status.HTTP_404_NOT_FOUND)

        if user.verify:
            return Response({'error': 'User is already verified'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_code = generate_random_otp()
            user.code = new_code
            user.save()

            sent_to = user.email
            message = user.code
            codeverify(sent_to, message)

            return Response({'message': 'Verification email resend successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Internal Server Error', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)










#Resetting Email
class ResetEmailView(APIView):
    authentication_classes = []

    

    def add_email_change_record(self, user, old_email):
        """
        Add a record of the old email address change to the email_changed field.
        """
        if not user.email_changed:
            user.email_changed = []

        timestamp = timezone.now()
        user.email_changed.append({'old_email': old_email, 'timestamp': timestamp.isoformat()})
        user.last_email_changed_at = timestamp
        user.save()

    @swagger_auto_schema(
        operation_description="Reset email with verification.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["old_email", "new_email", "password"],
            properties={
                'old_email': openapi.Schema(type=openapi.TYPE_STRING, description="Current email"),
                'new_email': openapi.Schema(type=openapi.TYPE_STRING, description="New email"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
            },
        ),
        responses={200: "Email updated", 400: "Bad Request", 401: "Unauthorized"}
    )

    def post(self, request):
        try:
            old_email = request.data.get('old_email')
            new_email = request.data.get('new_email')
            password = request.data.get('password')
            
            user = authenticate(request, email=old_email, password=password)
            if user is None:
                return Response({'error': 'Invalid old email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

            if UserAccount.objects.filter(email=new_email).exists() or \
               UserAccount.objects.filter(email_changed__contains=[{'old_email': new_email}]).exists():
                return Response({'error': 'The new email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)

            otp = generate_random_otp()

            user.email = new_email
            user.verify = False

            self.add_email_change_record(user, old_email)

            user.code = otp
            user.save()
            print(old_email, otp)
            code_verify_for_reset_email(old_email, otp)

            return Response({'message': 'Email updated successfully. OTP sent to the old email. Please verify it first.'}, status=status.HTTP_200_OK)
        except KeyError as e:
            return JsonResponse({'error': f'Missing key: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': f'{e} Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Reset Email Verification
class ResettingEmailVerify(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Verify reset email with code and email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["code", "email"],
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description="Verification code"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
            },
        ),
        responses={200: "Resetting email verified", 403: "Code mismatch", 404: "Email not found"}
    )

    def post(self,request):
      code = request.data['code']
      email = request.data['email']
      if UserAccount.objects.filter(email=email).exists():
         verify_code = UserAccount.objects.filter(email=email).values_list('code')[0][0]
         if verify_code == code:
            UserAccount.objects.filter(email=email).update(verify=True)
            verify = UserAccount.objects.filter(email=email).values_list('verify')[0][0]
            return Response({f'{verify}':'Resetting email Verified'},status=status.HTTP_200_OK)
         else:
            return Response('Code mismatch',status=status.HTTP_403_FORBIDDEN)
      else:
         return Response('This email does not exist',status=status.HTTP_404_NOT_FOUND)
      



class ForgotPasswordAPIView(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Send password reset link to email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
            },
        ),
        responses={200: "Password reset link sent", 404: "User not found"}
    )

    def post(self, request):
        try:
            email = request.data.get('email')
            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = UserAccount.objects.get(email=email)
            except UserAccount.DoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # reset_password_link = reverse('reset-password') + f'?uid={uid}&token={token}'
            reset_password_link = request.build_absolute_uri(
                reverse('reset-password') + f'?uid={uid}&token={token}'
            )
            # reset_password_link = 'https://blueparrotai.com/api/auth/reset-password/' + f'?uid={uid}&token={token}'

            print(reset_password_link)

            subject = 'Reset Your Password'
            message = f'Hello {email},\n\nYou can reset your password by clicking the following link:\n\n{reset_password_link}'
            send_html_email(subject, email, reset_password_link)

            return Response({'message': 'Password reset link has been sent to your email'})
        except KeyError as e:
            return JsonResponse({'error': f'Missing key: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': f'{e} Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class ResetPasswordAPIView(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Reset password using uid, token, and new password.",
        manual_parameters=[
            openapi.Parameter('uid', openapi.IN_QUERY, description="Encoded user ID", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('token', openapi.IN_QUERY, description="Password reset token", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('new_password', openapi.IN_QUERY, description="New password", type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: "Password reset successful", 400: "Invalid reset link"}
    )

    def post(self, request):
        try:
            uidb64 = request.query_params.get('uid')
            token = request.query_params.get('token')
            new_password = request.query_params.get('new_password')

            print(uidb64)
            print(token)

            uid = force_str(urlsafe_base64_decode(uidb64))

            print(uid)

            try:
                user = UserAccount.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.user_password = new_password
                user.save()
                return Response({'message': 'Password reset successfully'})
            else:
                return Response({'error': 'Invalid password reset link'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'error': f'Missing key: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'{e} Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class CustomProviderAuthView(ProviderAuthView):
    authentication_classes = []


    @swagger_auto_schema(
        operation_summary="Authenticate user with Google OAuth2",
        operation_description="""
        Handles Google OAuth2 callback and sets access/refresh tokens in cookies.
        - If `state` matches an active session, the request proceeds.
        - If user exists (by email), new tokens are generated.
        - If successful, cookies `access` and `refresh` are set.
        """,
        manual_parameters=[
            openapi.Parameter(
                "state",
                openapi.IN_QUERY,
                description="Google OAuth2 state parameter",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User email (optional, used if state session not matched)")
            }
        ),
        responses={
            200: openapi.Response(
                description="Tokens returned successfully",
                examples={
                    "application/json": {
                        "access": "jwt-access-token",
                        "refresh": "jwt-refresh-token",
                        "role": "user"
                    }
                }
            ),
            201: openapi.Response(
                description="User authenticated successfully and tokens set in cookies"
            ),
            500: openapi.Response(
                description="Server error",
                examples={
                    "application/json": {"error": "Error message here"}
                }
            ),
        }
    )

    def post(self, request, *args, **kwargs):
        request.GET = request.GET.copy()
        received_state = request.query_params.get("state")
        
        valid_sessions = Session.objects.filter(expire_date__gte=now())
        found_matching_state = False
        
        for session in valid_sessions:
            session_data = session.get_decoded()
            session_state = session_data.get("google-oauth2_state")
            
            print(f"Checking session: {session.session_key}, State: {session_state}")
            
            if session_state == received_state:
                found_matching_state = True
                request.session = session.get_decoded()
                print(f"Found matching state in session: {session.session_key}")
                break
        
        print(f"Received state: {received_state}")
        print(f"Found matching state: {found_matching_state}")
        
        if not found_matching_state:
            print(f"Warning: No matching state found in any session")
        response = super().post(request, *args, **kwargs)

        try:
            if response.status_code == 201:
                access_token = response.data.get('access')
                refresh_token = response.data.get('refresh')

                response.set_cookie(
                    'access',
                    access_token,
                    max_age=settings.AUTH_COOKIE_MAX_AGE,
                    path=settings.AUTH_COOKIE_PATH,
                    secure=settings.AUTH_COOKIE_SECURE,
                    httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                    samesite=settings.AUTH_COOKIE_SAMESITE
                )
                response.set_cookie(
                    'refresh',
                    refresh_token,
                    max_age=settings.AUTH_COOKIE_MAX_AGE,
                    path=settings.AUTH_COOKIE_PATH,
                    secure=settings.AUTH_COOKIE_SECURE,
                    httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                    samesite=settings.AUTH_COOKIE_SAMESITE
                )

                logger.info("Access and refresh tokens set in cookies.")
                return response

            email = request.data.get("email")
            logger.info(f"Checking email: {email}")

            if email:
                try:
                    user = UserAccount.objects.get(email=email)
                    refresh = RefreshToken.for_user(user)
                    logger.info(f"Generated tokens for user: {email}")

                    response_data = {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "role": user.role
                    }

                    response = Response(response_data, status=status.HTTP_200_OK)
                    response.set_cookie(
                        'access', response_data["access"],
                        max_age=settings.AUTH_COOKIE_MAX_AGE,
                        path=settings.AUTH_COOKIE_PATH,
                        secure=settings.AUTH_COOKIE_SECURE,
                        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                        samesite=settings.AUTH_COOKIE_SAMESITE
                    )
                    response.set_cookie(
                        'refresh', response_data["refresh"],
                        max_age=settings.AUTH_COOKIE_MAX_AGE,
                        path=settings.AUTH_COOKIE_PATH,
                        secure=settings.AUTH_COOKIE_SECURE,
                        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                        samesite=settings.AUTH_COOKIE_SAMESITE
                    )
                    return response
                except UserAccount.DoesNotExist:
                    logger.warning(f"User not found for email: {email}")

            return response

        except Exception as e:
            logger.error(f"Error in POST request: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class WalletBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]


    @swagger_auto_schema(
        operation_summary="Retrieve wallet balance",
        operation_description="Get the wallet balance details for the authenticated user.",
        responses={
            200: openapi.Response(
                description="Wallet balance retrieved successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "user": 5,
                        "balance": "1500.50"
                    }
                }
            ),
            404: openapi.Response(
                description="Wallet not found for the user.",
                examples={
                    "application/json": {
                        "error": "Wallet not found for the user."
                    }
                }
            ),
            500: openapi.Response(
                description="Unexpected error",
                examples={
                    "application/json": {
                        "error": "An unexpected error occurred.",
                        "details": "Some error details here"
                    }
                }
            ),
        }
    )

    def get(self, request):
        try:
            wallet = request.user.wallet
            serializer = UserWalletSerializer(wallet)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except UserWallet.DoesNotExist:
            return Response({'error': 'Wallet not found for the user.'},status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': 'An unexpected error occurred.', 'details': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class RechargeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Recharge wallet.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["amount"],
            properties={
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, format="decimal", description="Recharge amount"),
            },
        ),
        responses={200: "Recharge successful", 400: "Invalid request"}
    )

    def post(self, request):
        try:
            user = request.user
            amount = request.data.get('amount')

            if not amount:
                return Response({'error': 'Amount is required.'}, status=status.HTTP_400_BAD_REQUEST)

            amount = Decimal(amount)

            is_first_recharge = not Recharge.objects.filter(user=user).exists()

            if is_first_recharge and amount < Decimal('300.00'):
                return Response({'error': 'First recharge must be ₹300 or more.'}, status=status.HTTP_400_BAD_REQUEST)

            if is_first_recharge:
                reward_referral_chain(user)

            wallet, _ = UserWallet.objects.get_or_create(user=user)
            wallet.balance += amount
            wallet.save()

            Recharge.objects.create(user=user, amount=amount)

            return Response({'message': 'Recharge successful'}, status=status.HTTP_200_OK)

        except InvalidOperation:
            return Response({'error': 'Invalid amount format.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
