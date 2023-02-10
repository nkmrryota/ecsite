from django.urls import path
from .views import (
    RegistUserView, HomeView, UserLoginView,
    UserLogoutView, UserView, UserCheckView,
    UserInformView, UserInformListView, UserUpdateView,
    UserAddressList,UserAddressDelete,UserConfigList,
    PasswordChange,PasswordChangeDone,
)

app_name = 'accounts'
urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
    path('user/', UserView.as_view(), name='user'),
    path('user_check/', UserCheckView.as_view(), name='user_check'),
    path('user_info/', UserInformView.as_view(), name='user_info'),
    path('user_inform_list/', UserInformListView.as_view(), name='user_inform_list'),
    path('user_update/<int:pk>', UserUpdateView.as_view(), name='user_update'),
    path('user_update/<int:pk>', UserUpdateView.as_view(), name='user_update'),
    path('user_address_list/', UserAddressList.as_view(), name='user_address_list'),
    path('user_address_delete/<int:pk>', UserAddressDelete.as_view(), name='user_address_delete'),
    path('userconfig_list', UserConfigList.as_view(), name='userconfig_list'),
    path('password_change', PasswordChange.as_view(), name='password_change'),
    path('password_change_done', PasswordChangeDone.as_view(), name='password_change_done'),
]
