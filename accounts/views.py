from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic.edit import CreateView, FormView, UpdateView, DeleteView
from django.views.generic.base import TemplateView, View
from .forms import RegistForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import UserCheckForm, UserInfoForm, UserUpdateForm
from stores.models import Addresses, OrderItems
from .models import Users
from django.views.generic.list import ListView
from django.contrib.auth import update_session_auth_hash
import os
from django.conf import settings

from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
)
from .forms import (
     UserUpdateForm, MyPasswordChangeForm
)


class HomeView(TemplateView):
    template_name = 'home.html'
    

class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = RegistForm


class UserLoginView(LoginView):
    template_name = 'user_login.html'
    authentication_form = UserLoginForm

    # ログインに成功した時
    def form_valid(self, form):
        remember = form.cleaned_data['remember']
        # #ログイン時session(username)に名前を保持する
        # self.request.session['username'] = self.request.username
        if remember:
            self.request.session.set_expiry(86400)

        return super().form_valid(form)


class UserLogoutView(LogoutView):
    pass


class UserView(LoginRequiredMixin, TemplateView):
    template_name = 'user.html'

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)







class UserCheckView(LoginRequiredMixin, FormView):
    """ 入力画面で確認ボタンが押下された時の処理を定義するView """
    template_name = 'user_check.html'  
    form_class = UserCheckForm         
    success_url = reverse_lazy('accounts:user_inform_list')  
    
 
    def form_valid(self, form):
        """ フォームの入力チェックを行い、エラーがない場合 """
        user_password = form.cleaned_data['password']
        login_user = self.request.user
        if login_user.check_password(user_password):
            # login(self.request, user_password)
            # login_user.set_password(user_password)
            # login_user = authenticate(self.request,email=self.request.user.email, password=user_password)
            # login(self.request, login_user)
            
            context = {
                'input_form_success': '入力が一致しました',
            }
            
            return super().form_valid(form)
        
        #入力パスワードが異なれば
        else:
            context = {
                'input_form_fail': 'パスワードを再入力してください',
                #失敗しても入力フォームが表示して打てるようにformも渡す
                'form' : form
            }
            return render(self.request, 'user_check.html', context)
    


# class UserCheckSuccessView(LoginRequiredMixin,TemplateView):
#     template_name = 'usercheck_success.html'

class UserInformView(LoginRequiredMixin, CreateView):
    template_name = "user_info.html"
    form_class = UserInfoForm
    success_url = reverse_lazy('accounts:home')

    def form_valid(self, form):
        form.user = self.request.user
        return super().form_valid(form)

class UserInformListView(LoginRequiredMixin, ListView):
    template_name = "user_Inform_list.html"
    model = Users
    

    # def get_queryset(self):
        # query = super().get_queryset()
        # user_obj = self.request.user
        # query = query.filter(
        #                 # icontainsで部分一致
        #                 id=user_obj.id
        #             )       

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.request.user.id

        context['user_pk'] = pk
        context['user'] = Users.objects.filter(
            pk=pk
        )
        user = Users.objects.filter(
            pk=pk
        )

        context['addresses'] = Addresses.objects.filter(
            user__pk=pk
        )
        context['orders'] = OrderItems.objects.filter(
            order__user_id = pk
        )[:3]
        
        return context

class UserConfigList(LoginRequiredMixin,TemplateView):
    template_name = 'userconfig_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.request.user.id
        context['user_pk'] = pk
        context['user'] = Users.objects.filter(
            pk=pk
        )
        context['addresses'] = Addresses.objects.filter(
            user__pk=pk
        )
        
        return context



class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "user_update.html"
    form_class = UserUpdateForm
    model = Users
    # クラス変数の定義の際には、まだurls.pyが動いていないので名前が定義されていない。それを解決するために、遅延関数としてreverse_lazyを用意
    success_url = reverse_lazy('accounts:user_inform_list') 


class UserAddressList(LoginRequiredMixin, TemplateView):
    template_name = "user_address_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.request.user.id
        context['addresses'] = Addresses.objects.filter(
            user__pk=pk
        )
        context['name'] = self.request.user.username
        return context


class UserAddressDelete(LoginRequiredMixin, DeleteView):
    template_name = "user_address_delete.html"
    model = Addresses
    success_url = reverse_lazy('accounts:user_address_list') 







class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('accounts:password_change_done')
    template_name = 'password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'password_change_done.html'
