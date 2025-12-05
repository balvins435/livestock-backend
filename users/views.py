from django.shortcuts import render
from django.views import View
from .models import User

# Create your views here.
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import User, VerificationToken
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ProfileUpdateSerializer, ChangePasswordSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from .permissions import IsOwnerOrAdmin
from .utils import send_verification_email, send_password_reset_email


class RegisterView(APIView):
    """Register new user"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Create verification token
            token = secrets.token_urlsafe(32)
            VerificationToken.objects.create(
                user=user,
                token=token,
                token_type='email_verification',
                expires_at=timezone.now() + timedelta(days=1)
            )
            
            # Send verification email
            send_verification_email(user, token)
            
            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """Verify user email"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, token):
        try:
            verification = VerificationToken.objects.get(
                token=token,
                token_type='email_verification'
            )
            
            if not verification.is_valid:
                return Response(
                    {'error': 'Invalid or expired token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = verification.user
            user.is_verified = True
            user.save(update_fields=['is_verified'])
            
            verification.is_used = True
            verification.save(update_fields=['is_used'])
            
            return Response({'message': 'Email verified successfully'})
        
        except VerificationToken.DoesNotExist:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationView(APIView):
    """Resend verification email"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        if user.is_verified:
            return Response(
                {'message': 'Email already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Invalidate old tokens
        VerificationToken.objects.filter(
            user=user,
            token_type='email_verification',
            is_used=False
        ).update(is_used=True)
        
        # Create new token
        token = secrets.token_urlsafe(32)
        VerificationToken.objects.create(
            user=user,
            token=token,
            token_type='email_verification',
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        send_verification_email(user, token)
        
        return Response({'message': 'Verification email sent'})


class PasswordResetRequestView(APIView):
    """Request password reset"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Create reset token
                token = secrets.token_urlsafe(32)
                VerificationToken.objects.create(
                    user=user,
                    token=token,
                    token_type='password_reset',
                    expires_at=timezone.now() + timedelta(hours=1)
                )
                
                send_password_reset_email(user, token)
            
            except User.DoesNotExist:
                pass  # Don't reveal if email exists
            
            return Response({
                'message': 'If the email exists, a reset link has been sent'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Confirm password reset"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                reset_token = VerificationToken.objects.get(
                    token=token,
                    token_type='password_reset'
                )
                
                if not reset_token.is_valid:
                    return Response(
                        {'error': 'Invalid or expired token'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                
                reset_token.is_used = True
                reset_token.save(update_fields=['is_used'])
                
                return Response({'message': 'Password reset successful'})
            
            except VerificationToken.DoesNotExist:
                return Response(
                    {'error': 'Invalid token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get and update profile"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return ProfileUpdateSerializer
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change password"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Old password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({'message': 'Password changed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Logout user (blacklist token)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'})
        except Exception:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DeactivateAccountView(APIView):
    """Deactivate user account"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        return Response({'message': 'Account deactivated successfully'})


class UserListView(generics.ListAPIView):
    """List all users (Admin only)"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'admin':
            return User.objects.all()
        
        # Non-admins can only see themselves
        return User.objects.filter(id=user.id)