from django.urls import path, include
from . import views

urlpatterns = [
    path('signin', views.signin, name='signin'),
    path('logout/', views.logoutUser, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('manuscripts', views.manuscripts, name='manuscripts'),
    path('users', views.users, name='users'),
    path('requests', views.requests_view, name='requests'),
    path('visitor_index', views.visitor_index, name='visitor_index'),
    path('download' , views.send_email_download_request , name="download"),
    path('download/<token>/' , views.download , name="download"),
    
    
    path('<int:staff_id>/updatestaff/', views.updatestaff, name='updatestaff'),
    path('<int:user_id>/deleteusers/', views.delete_users, name='deleteusers'),
    path('<int:books_id>/deletebooks/', views.delete_books, name='deletebooks'),
    path('<int:book_id>/editbooks/', views.edit_books, name='editbooks'),
    path('<int:request_id>/deleterequest/', views.delete_request, name='deleterequest'),
    
    #path('increment_count' , views.increment_count , name="increment_count"),
    
    
    path('bsit', views.bsit, name='bsit'), 
    path('bsed', views.bsed, name='bsed'),
    path('beed', views.beed, name='beed'),
    path('bssw', views.bssw, name='bssw'),
    path('bapos', views.bapos, name='bapos'),
    path('baels', views.baels, name='baels'),
    path('bsm', views.bsm, name='bsm'),
    path('bsa', views.bsa, name='bsa'),
    path('bsf', views.bsf, name='bsf'),
    path('bses', views.bses, name='bses'),
    path('bsce', views.bsce, name='bsce'),
]