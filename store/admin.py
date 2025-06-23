from django.contrib import admin
from .models import Product, Category, Gallery, Specification, Size, Color, Cart, CartOrder, CartOrderItem, Coupons, Wishlist, Review, ProductFaq, Notification, Tax



class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 0


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 0

    
class SizeInline(admin.TabularInline):
    model = Size
    extra = 0


class ColorInline(admin.TabularInline):
    model = Color
    extra = 0




class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','title', 'price', 'category','shipping_amount', 'vendor', 'stock_qty', 'in_stock','featured']
    list_editable =['featured']
    list_filter = ['date']
    list_search = ['title']
    inlines = [GalleryInline, SpecificationInline, SizeInline, ColorInline,]






class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id','product', 'user', 'qty','price', 'sub_total', 'date', 'total']
    list_filter = ['date']
    list_search = ['cart_id']
    


class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['payment_status', 'order_status', 'total']
    list_display = ['oid', 'payment_status', 'order_status', 'total']

    


class CartOrderItemtAdmin(admin.ModelAdmin):
    list_display = ['order', 'product','qty', 'sub_total', 'total', 'date','oid']
    
    list_filter = ['date']
    list_search = ['oid']
   

class ProductFaqAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'product','email', 'active', 'date']
    list_editable =['active']
    list_filter = ['date','active']
    list_search = ['product']


class ReviewAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'product','rating', 'active', 'date']
    list_editable =['active']
    list_filter = ['date','active']
    list_search = ['product']


class WishlistAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'product','date']
    list_filter = ['date']
    list_search = ['product']


class NotificationAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'order','vendor', 'order_item', 'seen', 'date']
    list_editable =['seen',]
    list_filter = ['date']
    list_search = ['order']


class CouponsAdmin(admin.ModelAdmin):
    list_display = [ 'vendor', 'code', 'discount', 'active', 'date']
    list_editable =['active','discount']
    list_filter = ['date', 'discount']
    list_search = ['code']




admin.site.register(Product, ProductAdmin)
admin.site.register(Category)   
admin.site.register(Cart,CartAdmin)
admin.site.register(CartOrder,CartOrderAdmin)
admin.site.register(CartOrderItem,CartOrderItemtAdmin)
admin.site.register(ProductFaq,ProductFaqAdmin)
admin.site.register(Review,ReviewAdmin)
admin.site.register(Wishlist,WishlistAdmin)
admin.site.register(Coupons,CouponsAdmin)
admin.site.register(Notification,NotificationAdmin)
admin.site.register(Tax)    



