from django.urls import path
from . import views

urlpatterns = [
    path('sign-in/', views.sign_in, name='sign-in'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('reset-password/', views.reset_password, name='reset-password'),
    path('invite-member/', views.invite_member, name='invite-member'),
    path('delete-member/', views.delete_member, name='delete-member'),
    path('update-member-role/', views.update_member_role, name='update-member-role'),
    path('stats/role-wise-users/', views.role_wise_users, name='role-wise-users'),
    path('stats/org-wise-members/', views.org_wise_members, name='org-wise-members'),
    path('stats/org-role-wise-users/', views.org_role_wise_users, name='org-role-wise-users'),
]
