from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('screening/<int:screening_id>/book/', views.booking, name='booking'),
    path('my_tickets/', views.my_tickets, name='my_tickets'),
    path('ticket/<int:ticket_id>/cancel/', views.cancel_ticket, name='cancel_ticket'),
    path('movie/<int:pk>/edit/', views.MovieUpdateView.as_view(), name='movie_edit'),
    path('movie/create/', views.MovieCreateView.as_view(), name='movie_create'),
    path('movie/<int:movie_id>/screening/add/', views.ScreeningCreateView.as_view(), name='screening_create'),
    path('movie/<int:pk>/delete/', views.MovieDeleteView.as_view(), name='movie_delete'),
    path('ticket/<int:ticket_id>/download/', views.download_ticket, name='download_ticket'),
]