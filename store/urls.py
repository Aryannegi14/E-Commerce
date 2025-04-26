from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('sock/<int:sock_id>/', views.sock_detail, name='sock_detail'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart_view, name='cart_view'),
    path('add_to_cart/<int:sock_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('contact/', views.contact_us, name='contact_us'),
    path('profile/', views.profile_view, name='profile'),
    path('check-username-email/', views.check_username_email, name='check_username_email'),
    path('signup/', views.signup, name='signup'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('signin/', views.signin_view, name='signin'),
    path('update_quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),
    path('buy/', views.buy_view, name='buy_view'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('order/<int:order_id>/download_invoice/', views.download_invoice, name='download_invoice'),
]