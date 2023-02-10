from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.edit import (
    UpdateView, DeleteView, CreateView
)
from django.urls import reverse_lazy
from django.core.cache import cache
from django.db import transaction

import os
from .models import(
    Addresses, Products, Carts, CartItems,
    Orders, OrderItems, ProductPictures,ProductTypes,ProductEvaluations, EvaluationCul,
    ChekeoutProduct,ChekeoutPrice, Transaction
)
from .forms import(
    CartUpdateForm, AddressInputForm,
)
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views import View
import datetime 
from django.core.mail import EmailMessage
import io
import matplotlib.pyplot as plt
import numpy as np
from decimal import Decimal
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#filterはオブジェクトのリストとして返されるが、getはひとつのオブジェクトだけが返るので、フィルタの結果条件に一致するオブジェクトが複数ある場合や条件に一致するものが無い場合もエラー発生する
# get 関数はプライマリキーでデータを引く状況のように基本的には確実にデータがあって、 存在しない場合は何らかの予測していないことが発生すべき、という場合に利用するべき




class ProductListView(ListView):
    model = Products
    #データはobject_listに格納される
    # os.path.joinは引数のパスを結合する（stores/product_list.html）
    template_name = os.path.join('stores','product_list.html')
    

    # デフォルトだと全て取ってくるから、絞り込むためにget_querysetで処理する
    # get_queryset_メソッドはすべてのリクエストに対して呼び出され
    # 返された値が「object_list」としてHTMLテンプレートへ渡される
    def get_queryset(self):
        # productsモデルをqueryにオブジェクト化
        query = super().get_queryset()
        
        #リクエストGETされた場合,product_type_nameをgetして何もない場合はNoN
        product_name = self.request.GET.get('product_name', None)
        product_type_name = self.request.GET.get('product_type_name', None)
        product_price = self.request.GET.get('product_price', None)
        #文字を一つずつfilterにかけることで検索を緩くする
        # プスはプレステと一致しないが、一文字ずつ取ればプ一致、ス一致となる
        if product_name:
            str = list(product_name)
            for s in str:
                if product_name:
                    query = query.filter(
                        # icontainsで部分一致
                        name__icontains=s
                    )        
        # product_type_nameがgetできた場合のみ,queryから絞り込んでqueryを更新
        if product_type_name:
            str = list(product_type_name)
            for s in str:
                if product_type_name:    
                    query = query.filter(
                        #あるテーブルに外部キーを通して接続したテーブルのカラムで絞り込む場合は,
                        # filter(外部キー名__外部のテーブルのカラム名=絞り込みたい値)
                        product_type__name__icontains=s
                    )
                    
        # lteは指定地より同等か小さい、gteは指定地より同等か大きい,ltは未満
        if product_price:
            if product_price == "1":
                query = query.filter(
                price__lte=1500
            )
            elif product_price == "2":
                query = query.filter(
                price__lte=5000,price__gt=1500
            )
            elif product_price == "3":
                query = query.filter(
                price__lte=10000,price__gt=5000
            )
            elif product_price == "4":
                query = query.filter(
                price__lte=20000,price__gt=10000
            )
            elif product_price == "5":
                query = query.filter(
                price__gte=20000
            )
        # inputタグのnameがoreder_byの値を格納
        # order_by = self.request.GET.get('order_by', 0)
        # if order_by == '1':
        #     query = query.order_by('price')
        # elif order_by == '2':
        #     #   降順
        #     query = query.order_by('-price')
        # elif order_by == '3':
        #     #   降順
        #     query = query.order_by('related_evaluationcul__avarageevalu')
        # elif order_by == '4':
        #     #   降順
        #     query = query.order_by('-related_evaluationcul__avarageevalu')
        # return query
        # htmlでobject_listを使用する際,queryの内容を表示（listviewで実行されるqueryを変更）
        order_by_highprice = self.request.GET.get('order_by_highprice', None)
        order_by_rowprice = self.request.GET.get('order_by_rowprice', None)
        order_by_highevalu = self.request.GET.get('order_by_highevalu', None)
        if order_by_highprice:
            query = query.order_by('-price')
        elif order_by_rowprice:
            #   降順
            query = query.order_by('price')
        elif order_by_highevalu:
            #   降順
            query = query.order_by('-related_evaluationcul__avarageevalu')
        
        # all = query
        # eval_int = 0
        # eval_all = 0
        # eval_list = []
        # for count in all:
        #     eval_all += 1
        #     eval_int += count.related_evaluation.evalucount
        
        # eval_list.append(round(eval_int/eval_all))
        # print(eval_list)


        return query


        
    # get_context_dataはページが表示される時呼び出される
     #絞った時にキャッシュ残して値をフォームに表示しておく
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_type_name'] = self.request.GET.get('product_type_name', '')
        context['product_name'] = self.request.GET.get('product_name', None)
        

        # 商品名で絞りこみされていなければ、重複しないようにProductTypesから取得
        # context['product_type_name_all'] = None
        # if not context['product_name']:
        context['product_type_name_all'] = ProductTypes.objects.all
        # 商品名で絞りこみされている場合
        # elif context['product_name']:
        #     context['product_type_name_all'] = ProductTypes.objects.filter(
        #          name = ProductTypes
        #     )

        context['product_name'] = self.request.GET.get('product_name', '')
        p = self.request.GET.get('product_price', '')
        if p:
            if p == '1':
                context['product_price'] = "0〜1500円"
                context['product_price_number'] = "1"
            elif p == '2':
                context['product_price'] = "1500~5000円"
                context['product_price_number'] = "2"
            elif p == '3':
                context['product_price'] = "5000~10000円"
                context['product_price_number'] = "3"
            elif p == '4':
                context['product_price'] = "10000~20000円"
                context['product_price_number'] = "4"
            elif p == '5':
                context['product_price'] = "20000円以上"
                context['product_price_number'] = "5"
            elif p == '6':
                context['product_price'] = "全て"
                context['product_price_number'] = "6"

        radio_check = self.request.GET.get('product_price', 0)
        if radio_check == '1':
            context['one'] = True
        elif radio_check == '2':
            context['two'] = True
        elif radio_check == '3':
            context['three'] = True
        elif radio_check == '4':
            context['four'] = True
        elif radio_check == '5':
            context['five'] = True
        elif radio_check == '6':
            context['six'] = True

        order_by_highprice = self.request.GET.get('order_by_highprice', None)
        order_by_rowprice = self.request.GET.get('order_by_rowprice', None)
        order_by_highevalu = self.request.GET.get('order_by_highevalu', None)
        if order_by_highprice:
            context['order_by'] = ' ' + order_by_highprice
        elif order_by_rowprice:
            context['order_by'] = ' ' + order_by_rowprice
        elif order_by_highevalu:
            context['order_by'] = ' ' + order_by_highevalu

        

            
        return context


class ProductDetailView(DetailView):
    model = Products
    template_name = os.path.join('stores', 'product_detail.html')
    # context_object_nameでobjects名を変更することができる
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.kwargs['pk']
        
        context['is_added'] = CartItems.objects.filter(
            cart_id=self.request.user.id,
            product_id=kwargs.get('object').id
        ).first()
        evaluation = ProductEvaluations.objects.filter(
            product_id=kwargs.get('object').id
        )

        # クチコミ総数を取得
        total_count = 0
        for n in evaluation:
            total_count += 1
        context['total_count'] = total_count

        eval = []
        i = 0
        for e in evaluation:
            i += 1
            if i < 4:
                eval.append(e)

        context['evaluation'] = eval
        # check = OrderItems.objects.filter(
        #     order__user_id = self.request.user.id
        # )
        # if check:
        #     context['check'] = 1
        # else:
        #     context['check'] = 0

        eval_all = ProductEvaluations.objects.filter(
            product_id=self.kwargs['pk']
        )
        
        one = 0
        twe = 0
        three = 0
        fore = 0
        five = 0
        count = 0
        for int in eval_all:
            count += 1
            if int.evalucount == 1:
                one += 1
            elif int.evalucount == 2:
                twe += 1
            elif int.evalucount == 3:
                three += 1
            elif int.evalucount == 4:
                fore += 1
            elif int.evalucount == 5:
                five += 1
            
        one_round = str(round(Decimal(one/count*100))) + '%'
        twe_round = str(round(Decimal(twe/count*100))) + '%'
        three_round = str(round(Decimal(three/count*100))) + '%'
        fore_round = str(round(Decimal(fore/count*100))) + '%'
        five_round = str(round(Decimal(five/count*100))) + '%'
        context['one_round'] = one_round
        context['twe_round'] = twe_round
        context['three_round'] = three_round
        context['fore_round'] = fore_round
        context['five_round'] = five_round  
            
        One = float(one/count)
        Twe = float(twe/count)
        Three = float(three/count)
        Fore = float(fore/count)
        Five = float(five/count)
        context['one'] = One
        context['twe'] = Twe
        context['three'] = Three
        context['fore'] = Fore
        context['five'] = Five

        
        return context
    
# 条件を満たすとCartItemsに、アイテムを追加
def add_product(request):
    if request.is_ajax:
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        product = get_object_or_404(Products, id=product_id)
        if int(quantity) > product.stock:
            response = JsonResponse({'message': '在庫数を超えています'})
            response.status_code = 403
            return response
        if int(quantity) <= 0:
            response = JsonResponse({'message': '0より大きい値を入力してください'})
            response.status_code = 403
            return response
        cart = Carts.objects.get_or_create(
            user=request.user
        )
        #modelに記載のCartItemsManagerのsave_item関数を実行（save）
        if all([product_id, cart, quantity]):
            CartItems.objects.save_item(
                quantity=quantity, product_id=product_id,
                cart=cart[0]
            )
            return JsonResponse({'message': '商品をカートに追加しました'})



class EvaluForm(LoginRequiredMixin,CreateView):
    template_name = os.path.join('stores', 'evalu.html')
    model = ProductEvaluations
    # # 新しいのが上に行くよう並び替え
    # ordering = ('-created',)
    fields = ['subject', 'comment']
    success_url = reverse_lazy('accounts:home')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs['pk']
        context['id'] = id
        context['products'] = Products.objects.filter(
            id=id
        )
        return context

    # form_validは、フォームがエラーなく送信された際に発動するメソッド
    def form_valid(self, form):
        object = form.save(commit=False)
        product_id = self.request.POST['hidden_data']
        evalucount = self.request.POST.get('rate')
        object.user = self.request.user
        object.product_id = product_id
        object.evalucount = evalucount
        object.date = datetime.datetime.now()
        object.save()

        # product = Products.objects.filter(product_id=product_id)
        evalu_count = ProductEvaluations.objects.filter(product_id=product_id)
        evalcount = 0
        i = 0
        average = 0
        for count in evalu_count:
            evalcount += count.evalucount
            i += 1 
        average = evalcount / i  
        average = average

        EvaluationCul.objects.update_or_create(
                    product_id=product_id,
                    defaults={
                        'avarageevalu': average,
                    },
                )
        
        
        # スーパーメソッドを呼び出しバリデーション(form.is_valid)を行う
        return super().form_valid(form)


class EvaluList(ListView):
    model = ProductEvaluations
    template_name = os.path.join('stores','evalu_list.html')
    paginate_by = 8

    def get_queryset(self):
        query = super().get_queryset()

        product_id = self.kwargs['pk']
        query = query.filter(
                        product__id=product_id
                    )  
        query = query.order_by('-date')
        
        order_by_date = self.request.GET.get('order_by_date', None)
        order_by_review = self.request.GET.get('order_by_review', None)

        if order_by_date:
            query = query.order_by('-date')
        elif order_by_review:
            query = query.order_by('-evalucount')
        
        

        # paginator = Paginator(query, self.paginate_by)
        # page = self.request.GET.get('order_by_date')
        # try:
        #     page_obj = paginator.page(page)
        # except PageNotAnInteger:
        #     page_obj = paginator.page(1)
        # except EmptyPage:
        #     page_obj = paginator.page(paginator.num_pages)
        # return query
        #文字を一つずつfilterにかけることで検索を緩くする
        # プスはプレステと一致しないが、一文字ずつ取ればプ一致、ス一致となる
        # if product_name:
        #     str = list(product_name)
        #     for s in str:
        #         if product_name:
        #             query = query.filter(
        #                 # icontainsで部分一致
        #                 name__icontains=s
        #             )  
        # if order_by_date:
        #     query = query.order_by('-date')
        #     print(1)
        # elif order_by_review:
        #     query = query.order_by('-evalucount')

        
        
        # all = query
        # eval_int = 0
        # eval_all = 0
        # eval_list = []
        # for count in all:
        #     eval_all += 1
        #     eval_int += count.related_evaluation.evalucount
        
        # # eval_list.append(round(eval_int/eval_all))
        # # print(eval_list)
        # messages.add_message(self.request, messages.INFO, page_obj)

        return query


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        # order_by_date = self.request.GET.get('order_by_date', None)
        # order_by_review = self.request.GET.get('order_by_review', None)
        
        # if order_by_date:
        #     context['order_by_date'] = order_by_date
        
        # if order_by_date:
        #     context['order_by_review'] = order_by_date


        eval_all = ProductEvaluations.objects.filter(
            product_id=self.kwargs['pk']
        )
        
        one = 0
        twe = 0
        three = 0
        fore = 0
        five = 0
        count = 0
        for int in eval_all:
            count += 1
            if int.evalucount == 1:
                one += 1
            elif int.evalucount == 2:
                twe += 1
            elif int.evalucount == 3:
                three += 1
            elif int.evalucount == 4:
                fore += 1
            elif int.evalucount == 5:
                five += 1
            
        one_round = str(round(Decimal(one/count*100))) + '%'
        twe_round = str(round(Decimal(twe/count*100))) + '%'
        three_round = str(round(Decimal(three/count*100))) + '%'
        fore_round = str(round(Decimal(fore/count*100))) + '%'
        five_round = str(round(Decimal(five/count*100))) + '%'
        context['one_round'] = one_round
        context['twe_round'] = twe_round
        context['three_round'] = three_round
        context['fore_round'] = fore_round
        context['five_round'] = five_round  
            
        One = float(one/count)
        Twe = float(twe/count)
        Three = float(three/count)
        Fore = float(fore/count)
        Five = float(five/count)
        context['one'] = One
        context['twe'] = Twe
        context['three'] = Three
        context['fore'] = Fore
        context['five'] = Five

        check = OrderItems.objects.filter(
            order__user_id = self.request.user.id
        )
        if check:
            context['check'] = 1
        else:
            context['check'] = 0

        return context

    
    
    

# CartItemsからユーザーIDで絞り込んで取得したデータに対して在庫チェック等行い、対象ユーザーのカート内情報を
# contextに格納してreturn
class CartItemsView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('stores', 'cart_items.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        query = CartItems.objects.filter(cart_id=user_id)
        total_price = 0
        items = []
        for item in query.all():
            total_price += item.quantity * item.product.price
            picture = item.product.related_picture.first()
            picture = picture.picture if picture else None
            in_stock = True if item.product.stock >= item.quantity else False
            tmp_item = {
                'quantity': item.quantity,
                'picture': picture,
                'name': item.product.name,
                'id': item.id,
                'price': item.product.price,
                'in_stock': in_stock,
            }
            items.append(tmp_item)
        context['total_price'] = total_price
        context['items'] = items
        return context


class CartUpdateView(LoginRequiredMixin, UpdateView):
    template_name = os.path.join('stores', 'update_cart.html')
    form_class = CartUpdateForm
    model = CartItems
    # クラス変数の定義の際には、まだurls.pyが動いていないので名前が定義されていない。それを解決するために、遅延関数としてreverse_lazyを用意
    success_url = reverse_lazy('stores:cart_items')


class CartDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('stores', 'delete_cart.html')
    model = CartItems
    success_url = reverse_lazy('stores:cart_items')



        


class InputAddressView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('stores', 'input_address.html')
    form_class = AddressInputForm
    success_url = reverse_lazy('stores:confirm_order')

    # Cartsにユーザーのユーザーのカゴがなければ、エラー。
    def get(self, request, pk=None):
        cart = get_object_or_404(Carts, user_id=request.user.id)
        if not cart.cartitems_set.all():
            raise Http404('商品が入っていません')
        return super().get(request, pk)

    # cacheのsetはformsで行っている
    # chacheに格納されている値を取り出してcontextに格納し,html表示させる処理をおこなっている
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_addresses'] = Addresses.objects.filter(user_id=self.request.user.id)


        address = cache.get(f'address_user_{self.request.user.id}')
        pk = self.kwargs.get('pk')
        address = get_object_or_404(Addresses, user_id=self.request.user.id, pk=pk) if pk else address
        if address:
            context['form'].fields['zip_code'].initial = address.zip_code
            context['form'].fields['prefecture'].initial = address.prefecture
            context['form'].fields['address'].initial = address.address
        context['addresses'] = Addresses.objects.filter(user=self.request.user).all()
        return context

    #   送られた値が正しかった時の処理
    def form_valid(self, form):
        form.user = self.request.user
        return super().form_valid(form)










class ConfirmOrderView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('stores', 'confirm_order.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        address = cache.get(f'address_user_{self.request.user.id}')
        context['address'] = address
        # get_object_or_404データベースからデータを取得するためのメソッドになります。
        # データを取り出す際に、データが存在しないと自動的に404エラーを出してくれる
        cart = get_object_or_404(Carts, user_id=self.request.user.id)
        context['cart'] = cart
        total_price = 0
        items = []
        product_names = []
        product_emails = []
        for item in cart.cartitems_set.all():
            total_price += item.quantity * item.product.price
            picture = item.product.related_picture.first()
            picture = picture.picture if picture else None
            #製品ID取り出すためのネームキーを取得
            product_names.append(item.product.name)
            product_emails.append(item.product.email)
            context['product_names'] = product_names
            context['product_emails'] = product_emails
            tmp_item = {
                'quantity': item.quantity,
                'picture': picture,
                'name': item.product.name,
                'price': item.product.price,
                'id': item.id,
                'product_id': item.product.pk
            }
            items.append(tmp_item)
        context['product_pk'] = Products.objects.filter(name__in=product_names) 
        context['total_price'] = total_price
        context['items'] = items
        return context
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        address = context.get('address')
        cart = context.get('cart')
        total_price = context.get('total_price')
        if (not address) or (not cart) or (not total_price):
            raise Http404('注文処理でエラーが発生しました')
        for item in cart.cartitems_set.all():
            if item.quantity > item.product.stock:
                raise Http404('注文処理でエラーが発生しました')
        order = Orders.objects.insert_cart(cart, address, total_price)
        OrderItems.objects.insert_cart_items(cart, order,address)
        Products.objects.reduce_stock(cart)
        cart.delete()

        
        # カートアイテムず
        carts = context.get('product_names')
        product_name = []
        for name in carts:
            product_name.append(name)

        emails = context.get('product_emails')
        product_email = []
        for email in emails:
            product_email.append(email)

        

        



        send = settings.EMAIL_HOST_USER


        # 通知用メールに送信
        for name,email in zip(product_name, product_email):
            inquiry = [email]
            msg = EmailMessage(
                '製品購入のお知らせ',
                '出品商品' + name + 'が購入されました',
                send,
                inquiry,
            )
            msg.send()

        # 自動返信メール
        inquiry = [self.request.user.email]
        thanks = 'ご購入いただきありがとうございます'
        message = render_to_string('mail/complete.txt', context={
                'name': self.request.user.username,
                'product_name': product_name
            })
        
        msg = EmailMessage(
            thanks,
            message,
            send,
            inquiry,
        )
        msg.send()

        # else:
        #     params['message'] = '入力情報を確認し、再入力して下さい'
        #     params['form'] = form
            

        return redirect(reverse_lazy('stores:order_success'))


class OrderSuccessView(LoginRequiredMixin, TemplateView):

    template_name = os.path.join('stores', 'order_success.html')


class OrderList(LoginRequiredMixin,ListView):
    model = OrderItems
    template_name = os.path.join('stores','order_list.html')
    
    def get_queryset(self):
        # productsモデルをqueryにオブジェクト化
        query = super().get_queryset()

        pk = self.request.user.id
        query = query.filter(
                        # icontainsで部分一致
                        order__user__id=pk
                    ) 
        return query


def info(request):
    params = {'message': '', 'form': None}
    if request.method == 'POST':
        form = ModelFormInfo(request.POST)
        if form.is_valid():
            form.save()
            
            post_name = request.POST.get('name')
            post_subject = request.POST.get('subject')
            post_message = request.POST.get('message')
            post_inquirymail = request.POST.get('mail')
            post_phon = request.POST.get('phon')

            #送信用メールアドレス
            sender = settings.EMAIL_HOST_USER

            # 通知用メールアドレス
            noticemail = [settings.NOTICE_MAIL]
            
            # 通知用メールの本文
            message = render_to_string('mail/notice.txt', context={
                    'name': post_name,
                    'subject': post_subject,
                    'message': post_message,
                    'inquirymail': post_inquirymail,
                    'phon': post_phon,
                })

            # 通知用メールに送信
            msg = EmailMessage(
                'MSPからのお問合わせ',
                message,
                sender,
                noticemail,
            )
            msg.send()

            # 自動返信メール
            inquiry = [post_inquirymail]
            send = settings.EMAIL_HOST_USER
            thanks = 'お問い合せありがとうございます'
            message = render_to_string('mail/complete.txt', context={
                    'name': post_name,
                    'subject': post_subject,
                    'message': post_message,
                    'inquirymail': post_inquirymail,
                    'phon': post_phon,
                })
            
            msg = EmailMessage(
                thanks,
                message,
                send,
                inquiry,
            )
            msg.send()
            return redirect('form_app:complete')

        else:
            params['message'] = '入力情報を確認し、再入力して下さい'
            params['form'] = form

    else:
        params['form'] = ModelFormInfo()
    
    return render(request, 'formapp/form_page.html', params)










    # # Cartsにユーザーのユーザーのカゴがなければ、エラー。
    # def get(self, request, pk=None):m
    #     cart = get_object_or_404(Carts, user_id=request.user.id)
    #     if not cart.cartitems_set.all():
    #         raise Http404('商品が入っていません')
    #     return super().get(request, pk)

    # # cacheのsetはformsで行っている
    # # chacheに格納されている値を取り出してcontextに格納し,html表示させる処理をおこなっている
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     context['user_addresses'] = Addresses.objects.filter(user_id=self.request.user.id)


    #     address = cache.get(f'address_user_{self.request.user.id}')
    #     pk = self.kwargs.get('pk')
    #     address = get_object_or_404(Addresses, user_id=self.request.user.id, pk=pk) if pk else address
    #     if address:
    #         context['form'].fields['zip_code'].initial = address.zip_code
    #         context['form'].fields['prefecture'].initial = address.prefecture
    #         context['form'].fields['address'].initial = address.address
    #     context['addresses'] = Addresses.objects.filter(user=self.request.user).all()
    #     return context

    # #   送られた値が正しかった時の処理
    # def form_valid(self, form):
    #     form.user = self.request.user
    #     return super().form_valid(form)






# # STRIPEのシークレットキー
# stripe.api_key = 'sk_test_51MEBYWAw8ehnBwkvAJUoCaKKc0egK6Dy2l17PsfdndSOfVmRbzsN6H5LMFC9FnLvCFUKcKEDzdeSwTWzqDXNPaTz00sR0HyXdh'

# # WEBHOOKのシークレットキー
# endpoint_secret = 'whsec_6b889eb152a8c72c39902fa7cf69bbf109f8352e35701813c92120786f4addcb'

# # Stripeのパブリックキー
# STRIPE_PUBLIC_KEY = 'pk_test_51MEBYWAw8ehnBwkvYdpTHd8zSbT5HERoXzbrvGxcQS1mGOIzCoqDPGuX4W2iA7CToTd37xoh0NqJzFpXlBKQwgbJ00Zp6TpVew'

# # Stripeのシークレットキー
# STRIPE_SECRET_KEY = 'sk_test_51MEBYWAw8ehnBwkvAJUoCaKKc0egK6Dy2l17PsfdndSOfVmRbzsN6H5LMFC9FnLvCFUKcKEDzdeSwTWzqDXNPaTz00sR0HyXdh'




# # 決済画面
# class CreateCheckoutSessionView(DetailView):
#     model = Products

#     def post(self, request, *args, **kwargs):
#         # 商品PK取得
#         product_pk = self.kwargs['pk']
        
#         user_pk = self.request.user.id

#         user_cart = CartItems.objects.filter(cart__user_id=user_pk, product_id=product_pk)
#         for user in user_cart:
#             quantity = user.quantity
#             print(user.product.name)
#             price_id = ChekeoutProduct.objects.filter(name=user.product.name)
            
        
#         for ids in price_id:
#             id = ids.id
#             price_id = ChekeoutPrice.objects.filter(product_id=id)
        
#         for ids in price_id:
#             id = ids.stripe_price_id
             



#         # for ids in price_id:
#         #     id = ids.related_product_id
#         #     print(id)
        
        

        
            
        

#         # price_id = ChekeoutPrice.objects.filter(product_name=user.product.name)
            
#         #     for ids in price_id:
#         #         id = ids.stripe_price_id
        
#         # 対象のカートアイテム絞り込み
#         # user = user_cart.filter(product_pk=product_pk)

#         # productname = ChekeoutPrice.objects.filter(product_name=user_cart.)
#         # print(productname)





#         # ユーザーのカート情報を取得
#         # user_items = CartItems.objects.filter(cart__user_id=self.request.user.id)

#         # product_id = []
#         # カート内商品のpk取得
#         # for user_item in user_items:
#         #     product_id.append(user_item.product.id)


#         # chekeout_product_price = [] 
#         # stripe_price_idを取得
#         # for id in product_id:
#         #     price = get_object_or_404(ChekeoutPrice, product_id=id)
#         #     chekeout_product_price.append(price.stripe_price_id)
#             # print(type(price.stripe_price_id))
#             # print(chekeout_product_price)

#          # quantityを取得
#         # chekeout_product_quantity = []
#         # for item in user_items:
#         #     chekeout_product_quantity.append(item.quantity)
#             # print(chekeout_product_quantity)
#             # print(type(item.quantity))

#         # zip関数で二つの配列を結合
#         # results = zip(chekeout_product_price, chekeout_product_quantity)


#         # # ドメイン
#         MY_DOMAIN = "http://127.0.0.1:8000/stores"

#         # 決済用セッション
#         # zip関数で二つの配列を結合
#         # for (product_price, product_quantity) in zip(chekeout_product_price, chekeout_product_quantity):
#         #     checkout_session = stripe.checkout.Session.create(
#         #         # 決済方法
#         #         payment_method_types=['card'],
#         #         # 決済詳細
#         #         line_items=[
#         #             {
#         #                 'price': product_price,       
#         #                 'quantity': product_quantity,                       
#         #             },

#         #         ],
#         #         # POSTリクエスト時にメタデータ取得
#         #         # metadata = {
#         #         #             "product_id":product.id,
#         #         #            },
#         #         mode='payment',                               # 決済手段（一括）

#         #         success_url=MY_DOMAIN + '/success/',        # 決済成功時のリダイレクト先
#         #         cancel_url=MY_DOMAIN + '/cancel/', 

#         #     )

#         checkout_session = stripe.checkout.Session.create(
#             # 決済方法
#             payment_method_types=['card'],
#             # 決済詳細
#             line_items=[
#                 {
#                     'price': id,       
#                     'quantity': quantity,                       
#                 },

#             ],
#                 # POSTリクエスト時にメタデータ取得
#                 # metadata = {
#                 #             "product_id":product.id,
#                 #            },
#             mode='payment',                               # 決済手段（一括）

#             success_url=MY_DOMAIN + '/success/',        # 決済成功時のリダイレクト先
#             cancel_url=MY_DOMAIN + '/cancel/', 

#         )
#         return redirect(checkout_session.url)


#         # for (product_price, product_quantity) in zip(chekeout_product_price, chekeout_product_quantity):
#         # checkout_session = stripe.checkout.Session.create(
#         #         # 決済方法
#         #     payment_method_types=['card'],
            
#         #         # 決済詳細
#         #     line_items=[
#         #         for (product_price, product_quantity) in zip(chekeout_product_price, chekeout_product_quantity):
#         #                 {
#         #                  'price': product_price,       
#         #                     'quantity': product_quantity,                       
#         #                 },

#         #     ],
#         #         # POSTリクエスト時にメタデータ取得
#         #         # metadata = {
#         #         #             "product_id":product.id,
#         #         #            },
#         #     mode='payment',                               # 決済手段（一括）

#         #     success_url=MY_DOMAIN + '/success/',        # 決済成功時のリダイレクト先
#         #     cancel_url=MY_DOMAIN + '/cancel/', 

#         # )




# # 決済成功画面
# class SuccessPageView(TemplateView):
#     template_name = os.path.join('stores', 'success.html')

# # 決済キャンセル画面
# class CancelPageView(TemplateView):
#     template_name = os.path.join('stores', 'cancel.html')




# # イベントハンドラ
# # Stripeでの顧客の購入イベントはstripe_webhook関数で検知(購入後の処理)
# @csrf_exempt
# def stripe_webhook(request):

#     # サーバーのイベントログからの出力ステートメント
#     # payload = request.body
#     payload = request.data
#     # sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     sig_header = request.headers['STRIPE_SIGNATURE']
#     event = None
#     try:
#         # 顧客のインベントログを取得
#         # endpoint_secretはwebhockキー
#         event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
#     except ValueError as e:
#         # 有効でないpayload
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         # 有効でない署名
#         return HttpResponse(status=400)

#     # checkout.session.completedイベント検知(顧客の商品決済完了イベントの検知)
#     # 決済時の顧客情報（顧客名・メールアドレス・購入商品・支払額など）を取得
#     if event['type'] == 'checkout.session.completed':
#         session = event['data']['object']
#     # if event['type'] == 'invoice.payment_succeeded':
#     #     invoice = event['data']['object']

#         # イベント情報取得
#         customer_name  = session["customer_details"]["name"]     # 顧客名
#         customer_email = session["customer_details"]["email"]    # 顧客メール
#         product_id     = session["metadata"]["product_id"]       # 購入商品ID
#         product        = ChekeoutProduct.objects.get(id=product_id)      # 購入商品情報
#         product_name   = product.name                            # 購入した商品名
#         amount         = session["amount_total"]                 # 購入金額（手数料抜き）

#         # 顧客の購入履歴を管理するトランザクションマスタにレコード挿入(DBに結果を保存)するための関数がSaveTransaction
#         # SaveTransaction(product_name, customer_name, customer_email, amount)


#         # 決済完了後メール送信（Djangoのメール機能利用）
#         send_mail(
#             subject = '商品購入完了！',                                                                                     # 件名
#             message = 'こんにちは',  # メール本文
#             recipient_list = ["nkmrryota87@gmail.com"],                                                                              # TO
#             from_email = 'ryoutancobu@gmail.com'                                                                                    # FROM
#         )
#         # 結果確認
#         print(session)
#         # print(invoice)

#     return HttpResponse(status=200)


# # 顧客の商品購入履歴を保存
# def SaveTransaction(product_name, customer_name, customer_email, amount):
#     # DB保存
#     saveData = Transaction.objects.get_or_create(
#                         product_name   =  product_name,
#                         date           = datetime.datetime.now(),
#                         customer_name  = customer_name,
#                         email          = customer_email,
#                         product_amount = amount
#                         )
#     return saveData