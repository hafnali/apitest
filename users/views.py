from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser,Organization, UserRole,models
from .serializers import UserSerializer, OrganizationSerializer, UserRoleSerializer
from django.core.mail import send_mail
from django.conf import settings

@api_view(['POST'])
def sign_in(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = CustomUser.objects.filter(username=username).first()
    if user and check_password(password, user.password):
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def sign_up(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        password = make_password(request.data.get('password'))
        user = CustomUser(username=request.data.get('username'), password=password)
        user.save()
        organization_serializer = OrganizationSerializer(data=request.data)
        if organization_serializer.is_valid():
            organization = organization_serializer.save()
            UserRole.objects.create(user=user, organization=organization, role='owner')
            send_mail(
                'Welcome!',
                'Thank you for signing up!',
                settings.DEFAULT_FROM_EMAIL,
                [user.username],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(organization_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def reset_password(request):
    username = request.data.get('username')
    new_password = request.data.get('new_password')
    user = CustomUser.objects.filter(username=username).first()
    if user:
        user.password = make_password(new_password)
        user.save()
        send_mail(
            'Password Updated',
            'Your password has been updated.',
            settings.DEFAULT_FROM_EMAIL,
            [user.username],
            fail_silently=False,
        )
        return Response({'detail': 'Password updated successfully'})
    return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def invite_member(request):
    username = request.data.get('username')
    user = CustomUser.objects.filter(username=username).first()
    if user:
        send_mail(
            'You are invited',
            'You have been invited to join our organization.',
            settings.DEFAULT_FROM_EMAIL,
            [user.username],
            fail_silently=False,
        )
        return Response({'detail': 'Invitation sent successfully'})
    return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_member(request):
    user_id = request.data.get('user_id')
    org_id = request.data.get('organization_id')
    user_role = UserRole.objects.filter(user_id=user_id, organization_id=org_id).first()
    if user_role:
        user_role.delete()
        return Response({'detail': 'Member deleted successfully'})
    return Response({'detail': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def update_member_role(request):
    user_id = request.data.get('user_id')
    org_id = request.data.get('organization_id')
    new_role = request.data.get('new_role')
    user_role = UserRole.objects.filter(user_id=user_id, organization_id=org_id).first()
    if user_role:
        user_role.role = new_role
        user_role.save()
        return Response({'detail': 'Member role updated successfully'})
    return Response({'detail': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def role_wise_users(request):
    roles = UserRole.objects.values('role').annotate(count=models.Count('id'))
    return Response(roles)

@api_view(['GET'])
def org_wise_members(request):
    orgs = UserRole.objects.values('organization__name').annotate(count=models.Count('id'))
    return Response(orgs)

@api_view(['GET'])
def org_role_wise_users(request):
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    status_filter = request.query_params.get('status')
    
    queryset = UserRole.objects.all()
    if from_date and to_date:
        queryset = queryset.filter(created_at__range=[from_date, to_date])
    if status_filter:
        queryset = queryset.filter(role=status_filter)
    
    result = queryset.values('organization__name', 'role').annotate(count=models.Count('id'))
    return Response(result)
