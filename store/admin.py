from django.contrib import admin
from .models import Sock, Review, Profile, Order, OrderItem

# Register Sock model
@admin.register(Sock)
class SockAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_in_stock')
    search_fields = ('name',)

# Register Review model
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'sock', 'text', 'rating', 'photo', 'video')
    search_fields = ('user__username', 'sock__name')
    list_filter = ('rating',)

# Register OrderItem model
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('sock', 'quantity', 'price')
    search_fields = ('sock__name',)

# Register Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_time', 'total_amount', 'payment_id', 'order_id', 'signature', 'status')
    list_filter = ('user', 'order_time', 'status')
    search_fields = ('user__username', 'payment_id', 'order_id')

# Register Profile model
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'pfp')
    search_fields = ('user__username',)