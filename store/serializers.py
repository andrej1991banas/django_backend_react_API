from rest_framework import serializers

from userauths.serializer import ProfileSerializer
from .models import Product, Category, Gallery, Specification, Size, Color, Cart, CartOrder, CartOrderItem, Coupons, Wishlist, Review, ProductFaq, Notification
from vendor.models import Vendor




#serializer for Category
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


#serializer for Gallery
class GallerySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Gallery
        fields = ['image']


#serializer for Specification
class SpecificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Specification
        fields = ['title', 'content']



#serializer for Size
class SizeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Size
        fields = ['name', 'price']


#serializer for Color
class ColorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Color
        fields = ['name', 'color_code']



#serializer for Gallery
class GallerySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Gallery
        fields = "__all__"



#serializer for Product
class ProductSerializer(serializers.ModelSerializer):
    gallery = GallerySerializer(many=True, read_only=True)
    color = ColorSerializer(many=True, read_only=True)
    size = SizeSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    specification = SpecificationSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'image',
            'description',
            'category',
            'price',
            'old_price',
            'shipping_amount',
            'stock_qty',
            'in_stock',
            'status',
            'featured',
            'views',
            'rating',
            'vendor',
            #reference to the Product.fucntions
            'gallery', 
            'color',
            'size',
            'specification',
            'product_rating', #getting function from the model and getting whatever result we getting fromm the func
            'rating_count',

            'pid',
            'slug',
            'date',
        ]

    #function for unpack the data in the arrays, to deeper levels of the data
    def __init__(self, *args, **kwargs):
        super(ProductSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method=="POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3



#serializer for Cart
class CartSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Cart
        fields = "__all__"
    #function for unpack the data in the arrays, to deeper levels of the data
    def __init__(self, *args, **kwargs):
        super(CartSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method=="POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3



#serializer for CartOrderItem
class CartOrderItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CartOrderItem
        fields = "__all__"
    #function for unpack the data in the arrays, to deeper levels of the data
    def __init__(self, *args, **kwargs):
        super(CartOrderItemSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method=="POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3



#serializer for CartOrder
class CartOrderSerializer(serializers.ModelSerializer):
    orderitem = CartOrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = CartOrder
        fields = "__all__"
    #function for unpack the data in the arrays, to deeper levels of the data
    def __init__(self, *args, **kwargs):
        super(CartOrderSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method=="POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3



#serializer for ProductFaq
class ProductFaqSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductFaq
        fields = "__all__"
    #function for unpack the data in the arrays, to deeper levels of the data
    def __init__(self, *args, **kwargs):
        super(ProductFaqSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method=="POST":
            self.Meta.depth = 0
        else: 
            self.Meta.depth = 3



#serializer for Vendor
class VendorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Vendor
        fields = "__all__"
    #function for unpack the data in the arrays, to deeper levels of the data
    def __init__(self, *args, **kwargs):
        super(VendorSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method=="POST":
            self.Meta.depth = 0
        else: 
            self.Meta.depth = 3



#serializer for Review
class ReviewSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = Review
        fields = [
            'id',
            'product',
            'user',
            'rating',
            'reply',
            'review',
            'date',
            'active',
            'profile',
        ]
    #function for unpack the data in the arrays, to deeper levels of the data
    def __init__(self, *args, **kwargs):
        super(ReviewSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method=="POST":
            self.Meta.depth = 0
        else: 
            self.Meta.depth = 3



#serializer for Wishlist
class WishlistSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Wishlist
        fields = "__all__"
    #function for unpack the data in the arrays, to deeper levels of the data
    def __init__(self, *args, **kwargs):
        super(WishlistSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method=="POST":
            self.Meta.depth = 0
        else: 
            self.Meta.depth = 3


#serializer for Coupons
class CouponsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Coupons
        fields = "__all__"
    #function for unpack the data in the arrays, to deeper levels of the data
    def __init__(self, *args, **kwargs):
        super(CouponsSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method=="POST":
            self.Meta.depth = 0
        else: 
            self.Meta.depth = 3



#serializer for Notification
class NotificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Notification
        fields = "__all__"
    #function for unpack the data in the arrays, to deeper levels of the data
    def __init__(self, *args, **kwargs):
        super(NotificationSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method=="POST":
            self.Meta.depth = 0
        else: 
            self.Meta.depth = 3 



class SummarySerializer(serializers.Serializer):
    products = serializers.IntegerField()
    orders = serializers.IntegerField()
    # customers = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)



class EarningSerializer(serializers.Serializer):
    monthly_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)

    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)




class CouponSummarySerializer(serializers.Serializer):
    total_coupons = serializers.IntegerField()
    total_active = serializers.IntegerField()




class NotificationSummarySerializer(serializers.Serializer):
    read_noti = serializers.IntegerField()
    unread_noti = serializers.IntegerField()
    all_noti = serializers.IntegerField()













