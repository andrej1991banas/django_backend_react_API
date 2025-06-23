from django.shortcuts import render, redirect
from django.conf import settings
from userauths.models import User, Profile
from userauths.serializer import ProfileSerializer
from store.models import Product, Category, Gallery, Specification, Size, Color, Cart, CartOrder, CartOrderItem, Coupons, Wishlist, Review, ProductFaq, Notification,Tax
from store.serializers import ProductFaqSerializer, CategorySerializer,VendorSerializer,WishlistSerializer, ProductSerializer, CartSerializer, CartOrderSerializer, CartOrderItemSerializer,CouponsSerializer, NotificationSerializer, ReviewSerializer,SummarySerializer, EarningSerializer, CouponSummarySerializer, NotificationSummarySerializer, SpecificationSerializer,ColorSerializer, SizeSerializer, GallerySerializer
from vendor.models import Vendor
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from decimal import Decimal
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import models, transaction
from rest_framework.decorators import api_view
from django.db.models.functions import ExtractMonth
from datetime import datetime, timedelta
from django.http import Http404





class DashboardStatsAPIView(generics.ListAPIView):
    serializer_class = SummarySerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        #Calculate summary values
        #get count od products with the same vendor
        product_counts = Product.objects.filter(vendor=vendor).count()
        #get count of orders with the same vendor
        order_count = CartOrder.objects.filter(vendor=vendor, payment_status="paid").count()
        #get count sum of ptotals in orders  with the same vendor
        revenue = CartOrderItem.objects.filter(vendor=vendor, order__payment_status="paid").aggregate(total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0
        #return data for serializator
        return [
            {
                "products": product_counts,
                "orders": order_count,
                "revenue": revenue,
            }
        ]
    
    
    def list(self, *args, **kwargs):
        #get queryset
        queryset = self.get_queryset()
        #get serialized data from get_wueryset function, passing more than one object so many=True
        serializer = self.get_serializer(queryset, many=True)
        #send data to frontend
        return Response(serializer.data)



#create API for rendering the couhnts for created orders by vendor in certai  month
@api_view (('GET',))
def MonthlyOrderChartAPIView(request, vendor_id):
    vendor=Vendor.objects.get(id=vendor_id)

    orders= CartOrder.objects.filter(vendor=vendor)
    #count and order  the created orders by months
    orders_per_month = orders.annotate(month=ExtractMonth("date")).values("month").annotate(orders=models.Count("id")).order_by("month")

    return Response(orders_per_month)

#create API for rendering the couhnts for created products by vendor in certai  month
@api_view (('GET',))
def MonthlyProductChartAPIView(request, vendor_id):
    vendor=Vendor.objects.get(id=vendor_id)

    products= Product.objects.filter(vendor=vendor)
    #count and order the created products by months
    products_per_month = products.annotate(month=ExtractMonth("date")).values("month").annotate(products=models.Count("id")).order_by("month")

    return Response(products_per_month)


class ProductAPIView(generics.ListAPIView):
    """ API view for product  from vendor perspective"""
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    #query for products filter by vendor_id
    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)
        return Product.objects.filter(vendor=vendor)
    

class OrderAPIView(generics.ListAPIView):
    """ API view for orders  from vendor perspective"""
    permission_classes = [AllowAny]
    serializer_class = CartOrderSerializer
    #query of products filtered by vendor_id
    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)
        return CartOrder.objects.filter(vendor=vendor, payment_status="paid")
    
    
class OrderdetailAPIView(generics.RetrieveAPIView):
    """ API view for order details  from vendor perspective"""
    permission_classes = [AllowAny]
    serializer_class = CartOrderSerializer

    #query of products filtered by vendor_id and order_oid
    def get_object(self):
        vendor_id = self.kwargs['vendor_id']
        order_oid = self.kwargs['order_oid']

        vendor = Vendor.objects.get(id=vendor_id)

        return CartOrder.objects.get(vendor=vendor, oid=order_oid)
    

class RevenueAPIView(generics.ListAPIView):
    """ API view for vendor revenue  from paid orders"""
    permission_classes = [AllowAny]
    serializer_class = CartOrderItemSerializer
    #qyery of cartOrderItems filtered by vendor, and returning the money "total_revenue" form "sub_total" data, 
    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        return CartOrderItem.objects.filter(vendor=vendor, order__payment_status="paid").aggregate(total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0  
   


class FilterOrderAPIView(generics.ListAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny] 

    def get_queryset(self, *args, **kwargs):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)
        #get filstered instance with the request
        filter = self.request.GET.get("filter")#get filter from URL by porduct status   


        #define conditions for filtering the orders 
        if filter == "paid":
            orders = CartOrder.objects.filter(vendor=vendor, payment_status="paid").order_by('-id')
        
        elif filter == "pending":
            orders = CartOrder.objects.filter(vendor=vendor, payment_status="pending").order_by('-id')
        
        elif filter == "processing":
            orders = CartOrder.objects.filter(vendor=vendor, payment_status="processing").order_by('-id')
        
        # elif filter == "cancelled":
        #     orders = CartOrder.objects.filter(vendor=vendor, payment_status="cancelled").order_by('-id')
        
        elif  filter == "latest":
            orders = CartOrder.objects.filter(vendor=vendor).order_by('-id')

        elif  filter == "oldest":
            orders = CartOrder.objects.filter(vendor=vendor).order_by('id')

        elif  filter == "pending":
            orders = CartOrder.objects.filter(vendor=vendor, order_status="pending").order_by('-id')

        elif  filter == "fullflled":
            orders = CartOrder.objects.filter(vendor=vendor, order_status="fullflled").order_by('-id')

        elif  filter == "cancelled":
            orders = CartOrder.objects.filter(vendor=vendor, order_status="cancelled").order_by('-id')

        return orders


class FilterProductAPIView(generics.ListAPIView):
    """ API view with definition of filtering the products from vendor with status data (stattes)"""
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)
        #get filstered instance with the request
        filter = self.request.GET.get("filter")#get filter from URL by porduct status


        #define conditions for filtering the products 
        if filter == "published":
            product = Product.objects.filter(vendor=vendor, status="published")

        elif filter == "in_review":
            product = Product.objects.filter(vendor=vendor, status="in_review")

        elif filter == "disabled":
            product = Product.objects.filter(vendor=vendor, status="disabled")

        elif filter == "draft":
            product = Product.objects.filter(vendor=vendor, status="draft")

        else:
            product = Product.objects.filter(vendor=vendor)

        return product
    


class EarningAPIView(generics.ListAPIView):
    """ API view for vendor revenue for one month from paid orders"""
    permission_classes = [AllowAny]
    serializer_class = EarningSerializer  


    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        #defining the one month revenue variable and set the instance of it, set the variable for cunting one month ago revenue
        one_month_ago = datetime.today() - timedelta(days=28)
        monthly_revenue = CartOrderItem.objects.filter(vendor=vendor, order__payment_status="paid", date__gte=one_month_ago).aggregate(total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0  
        total_revenue = CartOrderItem.objects.filter(vendor=vendor, order__payment_status="paid").aggregate(total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0  
        #creating serialized data for return to frontend
        return [
            {
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue
        }
        ]


    def list(self, *args, **kwargs):
        #get queryset
        queryset = self.get_queryset()
        #get serialized data from get_wueryset function, passing more than one object so many=True
        serializer = self.get_serializer(queryset, many=True)
        #send data to frontend
        return Response(serializer.data)
    

@api_view(('GET',)) 
def MonthlyEarningTracker(request, vendor_id):
    vendor = Vendor.objects.get(id=vendor_id)

    monthly_earning_tracker = (
        CartOrderItem.objects
        .filter(vendor=vendor, order__payment_status="paid")
        .annotate(month=ExtractMonth ("date"))
        .values("month")
        .annotate(
            sales_count = models.Sum("qty"),
            total_earning = models.Sum(models.F("sub_total") + models.F("shipping_amount"))
        ).order_by('-month')
    )

    return Response(monthly_earning_tracker)



class ReviewListAPIView(generics.ListAPIView):
    """ API view to ernder all reviews for vendor porducts"""
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)
        
        reviews= Review.objects.filter(product__vendor=vendor) #getting data for review via foreign key product__vendor
        print (reviews)
        return reviews


class ReviewDetailAPIView(generics.RetrieveUpdateAPIView):
    """ API view to render  review for vendor porduct"""

    serializer_class = ReviewSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        vendor_id = self.kwargs['vendor_id']
        review_id = self.kwargs['review_id']

        vendor = Vendor.objects.get(id=vendor_id)
        review = Review.objects.get(product__vendor=vendor, id=review_id)
        return review


class CouponListCreateAPIView(generics.ListCreateAPIView):
    """ API view to ernder all coupons for vendor"""
    serializer_class = CouponsSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)
        return Coupons.objects.filter(vendor=vendor) #getting data for coupon via foreign key vendor    
    
    def create(self, request, *args, **kwargs):

        payload = request.data
        vendor_id = payload['vendor_id']
        code = payload['code']
        discount = payload['discount']
        active = payload['active']



        vendor = Vendor.objects.get(id=vendor_id)
        Coupons.objects.create(
            vendor=vendor,
            code=code,
            discount=discount,
            active=(active.lower() == "true")
        )
        return Response ({"message": "Couon Created SUccessfuly"}, status=status.HTTP_201_CREATED)
    

class CouponDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    """ API view to render  coupon for vendor"""
    serializer_class = CouponsSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        vendor_id = self.kwargs['vendor_id']
        coupon_id = self.kwargs['coupon_id']

        vendor=Vendor.objects.get(id=vendor_id)
        coupon = Coupons.objects.get(vendor=vendor, id=coupon_id) #getting data for coupon 

        return coupon


class CouponStatsAPIView(generics.ListAPIView):
    """ API view to ernder all coupon stats for vendor"""
    serializer_class = CouponSummarySerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)


        total_coupons = Coupons.objects.filter(vendor=vendor).count()
        total_active = Coupons.objects.filter(vendor=vendor, active=True).count()
        #creating serialized data for return to frontend
        return [
            {
                'total_coupons' : total_coupons,
                'total_active' : total_active
            }
        ]

    def list(self, *args, **kwargs):
        #get queryset
        queryset = self.get_queryset()
        #get serialized data from get_wueryset function, passing more than one object so many=True
        serializer = self.get_serializer(queryset, many=True)
        #send data to frontend
        return Response(serializer.data)
    
    
class NotificationAPIView(generics.ListAPIView):
    """ API view to ernder all unseen notifications for vendor"""
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)
        return Notification.objects.filter(vendor=vendor, seen=False).order_by('-id') #getting data for notification 



class NotificationSummaryAPIView(generics.ListAPIView):
    """ API view to ernder all notification summary for vendor"""
    serializer_class = NotificationSummarySerializer
    permission_classes = [AllowAny] 

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)
        
        unread_noti = Notification.objects.filter(vendor=vendor, seen=False).count()
        read_noti = Notification.objects.filter(vendor=vendor, seen=True).count()
        all_noti = Notification.objects.filter(vendor=vendor).count()
        
        return [
            {
               "read_noti" : read_noti,
                "unread_noti" : unread_noti,
                "all_noti" : all_noti
            }
        ]

    def list(self, *args, **kwargs):
        #get queryset
        queryset = self.get_queryset()
        #get serialized data from get_wueryset function, passing more than one object so many=True
        serializer = self.get_serializer(queryset, many=True)
        #send data to frontend
        return Response(serializer.data)



class NotificationVendorMarkAsSeen(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        vendor_id = self.kwargs['vendor_id']
        noti_id = self.kwargs['noti_id']


        vendor = Vendor.objects.get(id=vendor_id)
        noti = Notification.objects.get(id=noti_id, vendor=vendor)
        noti.seen = True
        noti.save()

        return noti



class VendorProfileUpdateView(generics.RetrieveUpdateAPIView):
    """ View to retrieve and update vendor profile based on user_id """
    serializer_class = ProfileSerializer
    permission_classes = (AllowAny, )
    queryset = Profile.objects.all()

    def get_object(self):
        user_id = self.kwargs['pk']  # 'pk' corresponds to user_id from the URL
        try:
            # Fetch the profile associated with the user_id
            profile = Profile.objects.get(user__id=user_id)
        except Profile.DoesNotExist:
            raise Http404("Profile matching the user ID does not exist.")
        return profile




class ShopUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [AllowAny]



class ShopAPIView(generics.RetrieveAPIView):

    serializer_class = VendorSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        vendor_slug = self.kwargs['vendor_slug']
        return Vendor.objects.get(slug=vendor_slug)
    


class ShopProductAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        vendor_slug = self.kwargs['vendor_slug']
        vendor = Vendor.objects.get(slug=vendor_slug)
        return Product.objects.filter(vendor=vendor)




class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny,]
    queryset = Product.objects.all()

    
    #pass all data or nothing with .atomic
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)

        serializer.save()
        #retrieve instance of the product from serializer
        product_instance = serializer.instance
        #get data from fontend and add them to those viariables in backend
        specifications_data = []
        colors_data = []
        sizes_data = []
        gallery_data = []
        #as we get dicts we need to go thrpugh keys and values and get values
        for key, value in self.request.data.items():
            #finding the part of data from frontend with specifications and data for specifications
            if key.startswith('specifications') and '[title]' in key :
                index=key.split('[')[1].split(']')[0]
                #grabbing the value of the title key 
                title = value
                #grabbing data from key and value pair with key ewuals to content
                content_key = f'specifications[{index}][content]'
                content = self.request.data.get(content_key)
                specifications_data.append({'title' : title, 'content' : content})

            elif key.startswith('colors') and '[name]' in key:
                index=key.split('[')[1].split(']')[0]
                name = value
                color_code_key = f'colors[{index}][color_code]'
                color_code = self.request.data.get(color_code_key)
                colors_data.append({'name' : name, 'color_code' : color_code})

            elif key.startswith('sizes') and '[name]' in key:
                index=key.split('[')[1].split(']')[0]
                name = value
                price_key = f'sizes[{index}][price]'
                price = self.request.data.get(price_key)
                sizes_data.append({'name': name, 'price': price })

            elif key.startswith('gallery') and '[image]' in key:
                index=key.split('[')[1].split(']')[0]
                image = value
                gallery_data.append({'image': image })


        self.save_nested_data(product_instance, SpecificationSerializer, specifications_data)
        self.save_nested_data(product_instance, ColorSerializer, colors_data)
        self.save_nested_data(product_instance, SizeSerializer, sizes_data)
        self.save_nested_data(product_instance, GallerySerializer, gallery_data)

        

    def save_nested_data(self, product_instance, serializer_class, data):
        serializer = serializer_class(data=data, many=True, context={'product': product_instance})
        serializer.is_valid(raise_exception = True)

        serializer.save(product=product_instance)

       

class ProductUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny, )

    def get_object(self):
        vendor_id = self.kwargs['vendor_id']
        product_pid = self.kwargs['product_pid']

        vendor = Vendor.objects.get(id=vendor_id)
        product = Product.objects.get(vendor=vendor, pid=product_pid)
        return product

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        product = self.get_object()

        # Deserialize product data
        serializer = self.get_serializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Delete all existing nested data
        product.specification().delete()
        product.color().delete()
        product.size().delete()
        product.gallery().delete()

        specifications_data = []
        colors_data = []
        sizes_data = []
        gallery_data = []
        # Loop through the keys of self.request.data
        for key, value in self.request.data.items():
            # Example key: specifications[0][title]
            if key.startswith('specifications') and '[title]' in key:
                # Extract index from key
                index = key.split('[')[1].split(']')[0]
                title = value
                content_key = f'specifications[{index}][content]'
                content = self.request.data.get(content_key)
                specifications_data.append(
                    {'title': title, 'content': content})

            # Example key: colors[0][name]
            elif key.startswith('colors') and '[name]' in key:
                # Extract index from key
                index = key.split('[')[1].split(']')[0]
                name = value
                color_code_key = f'colors[{index}][color_code]'
                color_code = self.request.data.get(color_code_key)
                image_key = f'colors[{index}][image]'
                image = self.request.data.get(image_key)
                colors_data.append(
                    {'name': name, 'color_code': color_code, 'image': image})

            # Example key: sizes[0][name]
            elif key.startswith('sizes') and '[name]' in key:
                # Extract index from key
                index = key.split('[')[1].split(']')[0]
                name = value
                price_key = f'sizes[{index}][price]'
                price = self.request.data.get(price_key)
                sizes_data.append({'name': name, 'price': price})

            # Example key: gallery[0][image]
            elif key.startswith('gallery') and '[image]' in key:
                # Extract index from key
                index = key.split('[')[1].split(']')[0]
                image = value
                gallery_data.append({'image': image})

        # Log or print the data for debugging
        print('specifications_data:', specifications_data)
        print('colors_data:', colors_data)
        print('sizes_data:', sizes_data)
        print('gallery_data:', gallery_data)

        # Save nested serializers with the product instance
        self.save_nested_data(
            product, SpecificationSerializer, specifications_data)
        self.save_nested_data(product, ColorSerializer, colors_data)
        self.save_nested_data(product, SizeSerializer, sizes_data)
        self.save_nested_data(product, GallerySerializer, gallery_data)

        return Response({'message': 'Product Updated'}, status=status.HTTP_200_OK)

    def save_nested_data(self, product_instance, serializer_class, data):
        serializer = serializer_class(data=data, many=True, context={
                                      'product_instance': product_instance})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product_instance)

    serializer_class = ProductSerializer
    permission_classes = [AllowAny,]
    queryset = Product.objects.all()


    def get_object(self):
        vendor_id = self.kwargs['vendor_id']
        product_pid = self.kwargs['product_pid']

        vendor = Vendor.objects.get(id=vendor_id)
        product = Product.objects.get(pid=product_pid, vendor=vendor)
        return product
    

    
    #pass all data or nothing with .atomic
    @transaction.atomic
    def perform_update(self, request, *args, **kwargs):
        product = self.get_object()

        serializer = self.get_serializer(product, data = request.data)
        serializer.is_valid(raise_exception=True)
        self.perfom_update(serializer)

        # Delete all existing nested data
        product.specification().delete()
        product.color().delete()
        product.size().delete()
        product.gallery().delete()

        #get data from fontend and add them to those viariables in backend
        specifications_data = []
        colors_data = []
        sizes_data = []
        gallery_data = []
        #as we get dicts we need to go thrpugh keys and values and get values
        for key, value in self.request.data.items():
            #finding the part of data from frontend with specifications and data for specifications
            if key.startswith('specifications') and '[title]' in key :
                index=key.split('[')[1].split(']')[0]
                #grabbing the value of the title key 
                title = value
                #grabbing data from key and value pair with key ewuals to content
                content_key = f'specifications[{index}][content]'
                content = self.request.data.get(content_key)
                specifications_data.append({'title' : title, 'content' : content})

            elif key.startswith('colors') and '[name]' in key:
                index=key.split('[')[1].split(']')[0]
                name = value
                color_code_key = f'colors[{index}][color_code]'
                color_code = self.request.data.get(color_code_key)
                colors_data.append({'name' : name, 'color_code' : color_code})

            elif key.startswith('sizes') and '[name]' in key:
                index=key.split('[')[1].split(']')[0]
                name = value
                price_key = f'sizes[{index}][price]'
                price = self.request.data.get(price_key)
                sizes_data.append({'name': name, 'price': price })

            elif key.startswith('gallery') and '[image]' in key:
                index=key.split('[')[1].split(']')[0]
                image = value
                gallery_data.append({'image': image })


        self.save_nested_data(product, SpecificationSerializer, specifications_data)
        self.save_nested_data(product, ColorSerializer, colors_data)
        self.save_nested_data(product, SizeSerializer, sizes_data)
        self.save_nested_data(product, GallerySerializer, gallery_data)

       
        return Response({'message': 'Product Updated'}, status=status.HTTP_200_OK)

    def save_nested_data(self, product_instance, serializer_class, data):
        serializer = serializer_class(data=data, many=True, context={
                                      'product_instance': product_instance})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product_instance)



class ProductDeleteAPIView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny, )

    def get_object(self):
        vendor_id = self.kwargs['vendor_id']
        product_id = self.kwargs['product_pid']


        vendor = Vendor.objects.get(id=vendor_id)
        product = Product.objects.get(vendor=vendor, pid=product_id)
        return product
