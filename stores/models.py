from django.db import models
from accounts.models import Users
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime

class ProductTypes(models.Model):
    name = models.CharField(max_length=1000)

    class Meta:
        db_table = 'product_types'

    def __str__(self):
        return self.name


class Manufacturers(models.Model):
    name = models.CharField(max_length=1000)

    class Meta:
        db_table = 'manufacturers'
    
    def __str__(self):
        return self.name




class ProductsManager(models.Manager):

    def reduce_stock(self, cart):
        for item in cart.cartitems_set.all():
            update_stock = item.product.stock - item.quantity
            item.product.stock = update_stock
            item.product.save()

class Products(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    stock = models.IntegerField()
    comment = models.CharField(max_length=100)
    product_type = models.ForeignKey(
        ProductTypes, on_delete=models.CASCADE, related_name="related_product_type"
    )
    manufacturer = models.ForeignKey(
        Manufacturers, on_delete=models.CASCADE
    )
    objects = ProductsManager()
    email = models.EmailField(max_length=255)

    class Meta:
        db_table = 'products'
    
    def __str__(self):
        return self.name










# class EvaluationsManager(models.Manager):

#     def save_item(self, product_id, quantity, cart):
#         c = self.model(quantity=quantity, product_id=product_id, cart=cart)
#         c.save()

class ProductEvaluations(models.Model):
    subject = models.CharField(max_length=20)
    evalucount = models.IntegerField(
            validators=[MinValueValidator(1), MaxValueValidator(5)]
            )
    comment = models.CharField(max_length=150)
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, related_name='related_evaluation'
    )
    # 一応紐付けしておいた
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE
    )
    date = models.DateTimeField(blank=True, null=True)
    # object = EvaluationsManager()

    class Meta:
        db_table = 'product_evaluations'
    
    def __str__(self):
        return self.product.name + ": " + self.subject  


class EvaluationCul(models.Model):
    avarageevalu = models.FloatField()
    product = models.OneToOneField(
        Products, on_delete=models.CASCADE,related_name='related_evaluationcul'
    )
    # product_evalu = models.ForeignKey(
    #     ProductEvaluations, on_delete=models.CASCADE, related_name='related_evalu_col'
    # )

    class Meta:
        db_table = 'evaluation_cul'
    
    def __str__(self):
        return self.product.name + ': ' + str(self.avarageevalu)


# 一つのモデルクラスで複数のフィールドにForeignKeyを使うときの逆参照はrelated_nameを使う
class ProductPictures(models.Model):
    picture = models.FileField(upload_to='product_pictures/')
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE,related_name='related_picture'
    )
    order = models.IntegerField()

    class Meta:
        db_table = 'product_pictures'
        ordering = ['order']
    
    def __str__(self):
        return self.product.name + ': ' + str(self.order)



class Carts(models.Model):
    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        primary_key=True
    )

    class Meta:
        db_table = 'carts'




class CartItemsManager(models.Manager):

    def save_item(self, product_id, quantity, cart):
        c = self.model(quantity=quantity, product_id=product_id, cart=cart)
        c.save()

class CartItems(models.Model):
    quantity = models.PositiveIntegerField()
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE
    )
    cart = models.ForeignKey(
        Carts, on_delete=models.CASCADE
    )
    objects = CartItemsManager()

    class Meta:
        db_table = 'cart_items'
        unique_together = [['product', 'cart']]


class Addresses(models.Model):
    zip_code = models.CharField(max_length=8)
    prefecture = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    user = models.ForeignKey(
        Users,
        on_delete = models.CASCADE
    )

    class Meta:
        db_table = 'addresses'
        # 組み合わせで一意にする
        unique_together = [
            ['zip_code', 'prefecture', 'address', 'user']
        ]
    
    def __str__(self):
        return f'{self.zip_code} {self.prefecture} {self.address}'


class OrdersManager(models.Manager):

    def insert_cart(self, cart: Carts, address, total_price):
        return self.create(
            total_price=total_price,
            address=address,
            user=cart.user
        )

class Orders(models.Model):
    total_price = models.PositiveIntegerField()
    address = models.ForeignKey(
        Addresses,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    objects = OrdersManager()
    
    class Meta:
        db_table = 'orders'


class OrderItemsManager(models.Manager):

    def insert_cart_items(self, cart, order, address):
        for item in cart.cartitems_set.all():
            self.create(
                quantity=item.quantity,
                product=item.product,
                order=order,
                zip_code=address.zip_code,
                prefecture=address.prefecture,
                address=address.address,
                chekeout_date=datetime.datetime.now()
            )

#決済後確定情報
class OrderItems(models.Model):
    quantity = models.PositiveIntegerField()
    product = models.ForeignKey(
        Products,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    order = models.ForeignKey(
        Orders, on_delete=models.CASCADE, related_name='related_order'
    )
    chekeout_date = models.DateTimeField(blank=True, null=True)
    zip_code = models.CharField(max_length=8)
    prefecture = models.CharField(max_length=10)
    address = models.CharField(max_length=200)

    objects = OrderItemsManager()
    
    class Meta:
        db_table = 'order_items'
        unique_together = [['product', 'order']]
    




# 決済時商品マスタ

class ChekeoutProduct(models.Model):
    # 商品名
    name = models.CharField(max_length=100)
    # 商品概要
    description = models.CharField(max_length=255, blank=True, null=True)
    # 商品ID（★stripeの商品IDを値に用いる）
    # Stripeに登録する商品をDjango DBの商品レコードと紐づけるための商品ID
    stripe_product_id = models.CharField(max_length=100)
    # 商品写真登録用のファイル
    file = models.FileField(upload_to="checkout_pictures/", blank=True, null=True)
    # 商品詳細ページのリンク
    url  = models.URLField()
    
    product = models.OneToOneField(
        Products, on_delete=models.CASCADE
    )

    # admin画面で商品名表示
    def __str__(self):
        return self.name

# 価格マスタ
class ChekeoutPrice(models.Model):
    # 外部キーで商品マスタを紐付け
    product = models.ForeignKey(ChekeoutProduct, on_delete=models.CASCADE, related_name='related_product_id')
    # 価格ID（★stripeの価格IDを値に用いる）
    stripe_price_id = models.CharField(max_length=100)
    # 価格
    price = models.IntegerField(default=0)
    
    # Django画面に表示する価格
    def get_display_price(self):
        return self.price
    

    # トランザクションマスタ
class Transaction(models.Model):
    # 購入日
    date   = models.CharField(max_length=100)
    # 購入者
    customer_name = models.CharField(max_length=100)
    # 購入者のメールアドレス
    email  = models.EmailField(max_length=100)
    # 購入商品名
    product_name = models.CharField(max_length=100)
    # 支払い金額
    product_amount = models.IntegerField()

    # admin画面で商品名表示
    def __str__(self):
        return self.date + '_' + self.product_name  + '_' + self.customer_name