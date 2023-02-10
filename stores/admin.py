from django.contrib import admin
from .models import (
    ProductTypes, Manufacturers, Products,
    ProductPictures, ProductEvaluations,
    EvaluationCul,ChekeoutProduct,ChekeoutPrice,Transaction,OrderItems
)


admin.site.register(
    [ProductTypes, Manufacturers, Products, ProductPictures, ProductEvaluations, EvaluationCul, ChekeoutProduct,ChekeoutPrice,Transaction,OrderItems]
)