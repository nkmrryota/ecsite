from django import forms
from .models import Users
from stores.models import Addresses
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, PasswordChangeForm
)
from django.contrib.auth import get_user_model


class RegistForm(forms.ModelForm):
    username = forms.CharField(label='名前')
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

    class Meta:
        model = Users
        fields = ['username', 'email', 'password']
    
    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
    remember = forms.BooleanField(label='ログイン状態を保持する', required=False)


class UserCheckForm(forms.Form):
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())


class UserInfoForm(forms.ModelForm):
    address = forms.CharField(label='住所', widget=forms.TextInput(attrs={'size': '80'}))

    class Meta:
        model = Addresses
        fields = ['zip_code', 'prefecture', 'address']
        labels = {
            'zip_code': '郵便番号',
            'prefecture': '都道府県',
        }

    def save(self):
        #まだコミットはしない
        address = super().save(commit=False)
        # ログイン中のユーザーをaddressモデルのユーザーに格納
        address.user = self.user
        # addressがユニークならセーブ
        try:
            address.validate_unique()
            address.save()
        except ValidationError as e:
            address = get_object_or_404(
                Addresses, user=self.user,
                prefecture=address.prefecture,
                zip_code=address.zip_code,
                address=address.address
            )
            pass
        return address


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(label='名前')

    class Meta:
        model = Users
        fields = ['username']
    
    def save(self):
        obj = super().save(commit=True)
        return obj



class MyPasswordChangeForm(PasswordChangeForm):
    """パスワード変更フォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
