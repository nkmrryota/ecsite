from django.urls import path,include
from .views import (
    ProductListView, ProductDetailView, 
    add_product, CartItemsView, CartUpdateView,
    CartDeleteView, InputAddressView, ConfirmOrderView,
    OrderSuccessView,EvaluForm,EvaluList,OrderList
)
from . import views


app_name='stores'
urlpatterns = [
    path('product_list/', ProductListView.as_view(), name='product_list'),
    # クラスベースビューでは内部でpkという変数を保持し、その値を自動的に取得してクラスベースビューが保持している変数pkに代入。
    # クラスベースビューはpkに保存された値をプライマリーキーとして使用し、連携しているモデルのデータを読み出しする。
    # pkに保存されたデータをデータベースから探索し、発見したらそのレコードを取得し、
    # 取得されたレコードは変数objectに格納されてテンプレートに渡されます
    path('product_detail/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('add_product/', add_product, name='add_product'),
    path('cart_items/', CartItemsView.as_view(), name='cart_items'),
    path('update_cart/<int:pk>', CartUpdateView.as_view(), name='update_cart'),
    path('delete_cart/<int:pk>', CartDeleteView.as_view(), name='delete_cart'),
    path('input_address/', InputAddressView.as_view(), name='input_address'),
    path('input_address/<int:pk>', InputAddressView.as_view(), name='input_address'),
    path('confirm_order/', ConfirmOrderView.as_view(), name='confirm_order'),
    path('order_success/', OrderSuccessView.as_view(), name='order_success'),
    path('evalu/', EvaluForm.as_view(), name='evalu'),
    path('evalu/<int:pk>', EvaluForm.as_view(), name='evalu'),
    path('order_list/', OrderList.as_view(), name='order_list'),
    path('evalu_list/', EvaluList.as_view(), name='evalu_list'),
    path('evalu_list/<int:pk>', EvaluList.as_view(), name='evalu_list'),
    # path('evaluation_view/<int:pk>', EvaluationView.as_view(), name='evaluation_view'),
    # path("create_checkout_session/", CreateCheckoutSessionView.as_view(), name="create_checkout_session"), 
    # path("create_checkout_session/<int:pk>", CreateCheckoutSessionView.as_view(), name="create_checkout_session"),  
    # path("success/", SuccessPageView.as_view(), name="success"),                                                   
    # path("cancel/", CancelPageView.as_view(), name="cancel"),
    # path("webhook/", stripe_webhook, name="webhook"), 

]