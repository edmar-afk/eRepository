from django.urls import path, include
from . import views

urlpatterns = [
    path('signin', views.signin, name='signin'),
    path('logout/', views.logoutUser, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('manuscripts', views.manuscripts, name='manuscripts'),
    path('users', views.users, name='users'),
    path('requests', views.requests, name='requests'),
    path('visitor_index', views.visitor_index, name='visitor_index'),
    path('download' , views.send_email_download_request , name="download"),
    path('download/<token>/' , views.download , name="download"),
    
    path('<int:user_id>/deleteusers/', views.delete_users, name='deleteusers'),
    path('<int:books_id>/deletebooks/', views.delete_books, name='deletebooks'),
    path('<int:request_id>/deleterequest/', views.delete_request, name='deleterequest'),
    
    #path('increment_count' , views.increment_count , name="increment_count"),
]