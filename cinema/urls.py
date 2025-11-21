from django.urls import path
from . import views

app_name = 'cinema'

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('purchase/<int:screening_id>/', views.PurchaseView.as_view(), name='purchase'),
    path('purchase/success/<int:ticket_id>/', views.purchase_success, name='purchase_success'),
]