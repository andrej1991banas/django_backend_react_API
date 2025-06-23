from django.shortcuts import render, redirect
from django.conf import settings
from userauths.models import User
from .models import Product, Category, Gallery, Specification, Size, Color, Cart, CartOrder, CartOrderItem, Coupons, Wishlist, Review, ProductFaq, Notification,Tax
from .serializers import ProductFaqSerializer, CategorySerializer, ProductSerializer, CartSerializer, CartOrderSerializer, CartOrderItemSerializer,CouponsSerializer, NotificationSerializer, ReviewSerializer

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from decimal import Decimal
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string




import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def send_notification(user=None, vendor=None, order=None, order_item=None):
    Notification.objects.create(
        user=user,
        vendor=vendor,
        order=order,
        order_item=order_item,
    )





#creating APi as a query set of API
class CategoryListAPIView(generics.ListAPIView):
    #get all Category items
    queryset = Category.objects.all()
    #define wchich serializer to use 
    serializer_class = CategorySerializer
    #define who can see the API data
    permission_classes = [AllowAny,]



#creating APi as a query set of API
class ProductListAPIView(generics.ListAPIView):
    #get all Category items
    queryset = Product.objects.all()
    #define wchich serializer to use 
    serializer_class = ProductSerializer
    #define who can see the API data
    permission_classes = [AllowAny,]


#API for display data for only one Product
class ProductDetailAPIView(generics.RetrieveAPIView):
    #define wchich serializer to use 
    serializer_class = ProductSerializer
    #define who can see the API data
    permission_classes = [AllowAny,]

    #owerwriting the get_object default method
    def get_object(self):
        slug = self.kwargs['slug']
        # pk = self.kwargs.get("pk")
        return Product.objects.get(slug=slug)


#API for display data in the Cart
class CartAPIView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes= [AllowAny,]
    #define crete method for payload
    def create(self,request, *args, **kwargs):
        payload = request.data
        #after getting data form Post method, get defined data lower in the function
        product_id = payload['product_id']
        user_id = payload['user_id']
        qty = payload['qty']
        price = payload['price']
        shipping_amount = payload['shipping_amount']
        country = payload['country']
        size = payload['size']
        color = payload['color']
        cart_id = payload['cart_id']
       
        product = Product.objects.get(id=product_id)
        #chceck if the user is not guest otherwie continue with User None
        if user_id != "undefined":    
            user = User.objects.get(id=user_id)#link the user in Cart data with actual User
        else:
            user = None


        country_tax = Tax.objects.filter(country=country)
        if country_tax:
            tax_rate = country_tax.rate / 100
        else:
            tax_rate = 23.00 / 100
        
        cart = Cart.objects.filter(cart_id=cart_id, product=product).first()
        sub_total = Decimal(price) * int(qty)
        
        if cart:
            #update data with new data from Cart model
            cart.product = product
            cart.user = user
            cart.qty = qty
            cart.price = price
            cart.sub_total = sub_total #transfering data to float, as sub_total in the model is defined as DecimalField
            cart.shipping_amount = Decimal(shipping_amount) * int(qty) #transfering data to float, as sub_total in the model is defined as DecimalField
            cart.tax_fee = sub_total * Decimal(tax_rate) #transfering data to float, as sub_total in the model is defined as DecimalField
            cart.color = color
            cart.size = size
            cart.country = country
            cart.cart_id = cart_id

            service_fee_amount = 2 / 100 #variable for defining any service fees for the services like credit cards payment, etc
            cart.service_fee = Decimal(service_fee_amount) * cart.sub_total
            #total price for the whole cart, that will be charged to the customer 
            cart.total = cart.sub_total + cart.shipping_amount + cart.tax_fee + cart.service_fee 
            cart.save()

            return Response({"message": "Cart Updated Sucessfully"}, status = status.HTTP_200_OK)

        else:
            cart = Cart()
            #update data with new data from Cart model
            cart.product = product
            cart.user = user
            cart.qty = qty
            cart.price = price
            cart.sub_total = sub_total #transfering data to float, as sub_total in the model is defined as DecimalField
            cart.shipping_amount = Decimal(shipping_amount) * int(qty) #transfering data to float, as sub_total in the model is defined as DecimalField
            cart.tax_fee = sub_total *Decimal(tax_rate) #transfering data to float, as sub_total in the model is defined as DecimalField
            cart.color = color
            cart.size = size
            cart.country = country
            cart.cart_id = cart_id

            service_fee_amount = 2 / 100 #variable for defining any service fees for the services like credit cards payment, etc
            cart.service_fee = Decimal(service_fee_amount) * cart.sub_total
            #total price for the whole cart, that will be charged to the customer 
            cart.total = cart.sub_total + cart.shipping_amount + cart.tax_fee + cart.service_fee 
            cart.save()

            return Response({"message": "Cart Created Sucessfully"}, status = status.HTTP_201_CREATED)


# API for list the items in the cart and showing data from  that cart details 
class CartListView(generics.ListAPIView):
    # use serializer for Cart details and Cart model
    serializer_class = CartSerializer
    permission_classes = [AllowAny,]
    # fetch all carts in Cart model 
    queryset = Cart.objects.all()

    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        user_id = self.kwargs.get('user_id')
        # check if the user exists otherwise continue with no user details 
        if user_id is not None:
            user = User.objects.get(id=user_id)
            queryset = Cart.objects.filter(user=user, cart_id=cart_id)

        else:
            queryset = Cart.objects.filter(cart_id=cart_id)

        return queryset
    
# Api for details cart with calculated data for each item
class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [AllowAny,]
    lookup_field = "cart_id"

    def get_queryset(self):

        cart_id = self.kwargs['cart_id']
        user_id = self.kwargs.get('user_id')

         # check if the user exists otherwise continue with no user details 
        if user_id is not None:
            user = User.objects.get(id=user_id)
            queryset = Cart.objects.filter(user=user, cart_id=cart_id)

        else:
            queryset = Cart.objects.filter(cart_id=cart_id)

        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        total_shipping = 0.0
        total_tax = 0.0
        total_service_fee = 0.0
        total_sub_total = 0.0
        total_total = 0.0

        for cart_item in queryset:
            total_shipping += float(self.calcutale_shipping(cart_item))
            total_tax += float(self.calculate_tax(cart_item))
            total_service_fee += float(self.calculate_service_fee(cart_item))
            total_sub_total += float(self.calculate_sub_total(cart_item))
            total_total += float(self.calculate_total(cart_item))

        data = {
         'shipping' : total_shipping,
         'tax' : total_tax,
         'service_fee' : total_service_fee,
         'sub_total' : total_sub_total,
         'total' : total_total,
        }

        return Response(data)

# define custom function to get data for data variable 
    def calcutale_shipping(self, cart_item):
        return cart_item.shipping_amount
    
    def calculate_tax (self, cart_item):
        return cart_item.tax_fee
    
    def calculate_service_fee (self, cart_item):
        return cart_item.service_fee
    
    def calculate_sub_total (self, cart_item):
        return cart_item.sub_total

    def calculate_total (self, cart_item):
        return cart_item.total




class CartItemDeleteAPIView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    lookup_field = 'cart_id'
    permission_classes = [AllowAny]

        # function for getting the item we need accordng to id, cart_id, and user details if exists
    def get_object(self):
        cart_id = self.kwargs['cart_id']
        item_id = self.kwargs['item_id']
        user_id = self.kwargs.get('user_id')

        if user_id:
            user = User.objects.get(id=user_id)
            cart = Cart.objects.get(id=item_id, cart_id=cart_id, user=user,)

        else:
            cart=Cart.objects.get(id=item_id, cart_id=cart_id,)

        return cart




class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny,]
    queryset = CartOrder.objects.all()


    def create(self, request):
        payload = request.data

        full_name = payload['full_name']
        email = payload['email']
        mobile = payload['mobile']
        address = payload['address']
        city = payload['city']
        state = payload['state']
        country = payload['country']
        cart_id = payload['cart_id']
        user_id = payload['user_id']

        try:
            user = User.objects.get(id=user_id)
        except:
            user = None

        # grabbing all items in particular cart instance
        cart_items= Cart.objects.filter(cart_id=cart_id)

        total_shipping = Decimal(0.00)
        total_tax = Decimal(0.00)
        total_service_fee = Decimal(0.00)
        total_sub_total = Decimal(0.00)
        total_initial_total = Decimal(0.00)
        total_total = Decimal(0.00)

        order = CartOrder.objects.create(
            buyer = user,
            full_name =full_name,
            email = email,
            mobile = mobile,
            address = address,
            city = city,
            state = state,
            country =country,
        )

        for c in cart_items:
            CartOrderItem.objects.create(
                order = order,
                product = c.product,
                
                qty = c.qty,
                size = c.size,
                color = c.color,
                price = c.price,
                sub_total = c.sub_total,
                shipping_amount = c.shipping_amount,
                service_fee = c.service_fee,
                tax_fee = c.tax_fee,
                total = c.total,
                initial_total = c.total,
                vendor=c.product.vendor
                
            )

            total_shipping +=Decimal(c.shipping_amount)
            total_tax +=Decimal(c.tax_fee)
            total_service_fee +=Decimal(c.service_fee)
            total_sub_total +=Decimal(c.sub_total)
            total_initial_total +=Decimal(c.total)
            total_total +=Decimal(c.total)

            order.vendor.add(c.product.vendor)
        
        order.sub_total = total_sub_total
        order.shipping_amount = total_shipping
        order.tax_fee = total_tax
        order.service_fee = total_service_fee
        order.initial_total = total_initial_total
        order.total = total_total

        order.save()

        return Response({"message": "Order Created Successfully", "order_oid":order.oid}, status=status.HTTP_201_CREATED)
    

class CheckoutView(generics.RetrieveAPIView):
    serializer_class = CartOrderSerializer
    lookup_field = "order_oid"
    permission_classes = [AllowAny]

    #redefining the built in method get object
    def get_object(self):
        #get the data from order items for "order_oid"
        order_oid = self.kwargs['order_oid']
        #finding the order with specific oid
        order = CartOrder.objects.get(oid=order_oid)
        #return data to API
        return order
    

class CouponAPIView(generics.CreateAPIView):
    serializer_class = CouponsSerializer
    queryset = Coupons.objects.all()
    permission_classes = [AllowAny]
    

    def create(self, request):
        #get payload from request and use it
        # 
        payload = request.data
        #get data and define new variables for creation of the coupon model, getting data from the payload
        order_oid = payload['order_oid']
        coupon_code = payload['code']  
        print(order_oid)
        #finding the order with specific oid
        order = CartOrder.objects.get(oid=order_oid)
        coupon = Coupons.objects.filter(code=coupon_code).first() #choose first find if exists
        # print(order)
        print (coupon)
        if coupon:
            #find order and vendor tangled up with the coupon code 
            order_items = CartOrderItem.objects.filter(order=order, vendor=coupon.vendor)
            print (order_items)
            if order_items:
                #iterate through order items 
                for i in order_items:
                    #check if the coupon was ever already used
                    if not coupon in i.coupon.all():
                        #if not being used, use it and apply discount and update the total price
                        discount = i.total * coupon.discount / 100
                        #update the total price with minut amount of the discount
                        i.total -= discount
                        #update sub_total with discount
                        i.sub_total += discount
                        #add discount to the coupon model as used coupon
                        i.coupon.add(coupon)
                        #update CartOrder model with saved field and show user how much money was saved 
                        i.saved += discount

                        order.total -= discount
                        order.sub_total -= discount
                        order.saved += discount

                        i.save()
                        order.save()

                        return Response({"message" : "Coupon Applied Successfully", "icon": "success"}, status=status.HTTP_200_OK)

                    else:
                        return Response({"message" : "Coupon Already Applied", "icon": "warning"}, status=status.HTTP_200_OK)
            
            return Response({"message" : "Order Item Does Not Exists", "icon": "error"}, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "Invalid Coupon Code", "icon": "error"}, status=status.HTTP_200_OK)



        
class StripeCheckoutView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]

    queryset = CartOrder.objects.all()
    def create(self, *args, **kwargs):
        order_oid = self.kwargs['order_oid']
        order = CartOrder.objects.get(oid=order_oid)

        if not order:
            return Response ({"meesage" : "Order Not Found"}, status=status.HTTP_NOT_FOUND)
       
        try:
            checkout_session = stripe.checkout.Session.create(
                # define attributes for strippe payment process
                customer_email = order.email,
                payment_method_types = ['card'],
                line_items = [
                    {
                        'price_data': {'currency': 'eur', 'product_data' : {'name': order.full_name},
                                    'unit_amount': int(order.total *100)},
                        'quantity': 1,
                    
                    }],
                    mode = 'payment',
                    success_url = 'http://localhost:5173/payment-success/' + order.oid +'?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url = 'http://localhost:5173/payment-cancelled' + order.oid +'?session_id={CHECKOUT_SESSION_ID}',
                )

            order.stripe_session_id = checkout_session.id
            order.save()

            return redirect (checkout_session.url, code=303)
        # except stripe.error.CardError as e:
        except stripe.error.StripeError as e: 
            return Response({"error": f"Something went wrong while creating the checkout sesion: {str(e)}"})



class PaymentSuccessView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]
    queryset = CartOrder.objects.all()

    def create(self, request, *args, **kwargs):
        #get data sent from Reacto to backend
        payload = request.data
        #definingn what data fetch from paylad from React form data 
        order_oid=payload['order_oid']
        session_id = payload['session_id']

        #comparing data from frontend and filter them in backend to return data from backend, the data we need 
        order = CartOrder.objects.get(oid=order_oid)
        order_items = CartOrderItem.objects.filter(order=order)

        #
        if session_id != 'null':
            #get session id fro API response from stripe data 
            session = stripe.checkout.Session.retrieve(session_id)

            #check if the payment was successfull from strippe API, then change data in backend and show response message
            if session.payment_status == "paid":
                if order.payment_status == "pending":
                    order.payment_status='paid'
                    order.save()

                    #send notification to user/buyer
                    if order.buyer != None:
                        send_notification(user=order.buyer, order=order)

                    #send notification AND EMAIL    to vendors
                    for o in order_items:
                        send_notification(vendor=o.vendor, order=order, order_item=o)
                        context = {
                            'order': order,
                            'order_items': order_items,
                            'vendor': o.vendor,
                        }

                        subject="New Sale"
                        text_body = render_to_string('email/vendor_sale.txt', context) 
                        html_body = render_to_string('email/vendor_sale.html', context) 

                        msg = EmailMultiAlternatives(
                            subject = subject,
                            from_email = settings.DEFAULT_FROM_EMAIL,
                            to = [o.vendor.email],
                            body = text_body,
                        )

                        msg.attach_alternative(html_body, "text/html")
                        msg.send()


                    #send email to buyer
                    context = {
                        'order': order,
                        'order_items': order_items,
                    }

                    subject="Order Placed Successfuly"
                    text_body = render_to_string('email/order_placed.txt', context) 
                    html_body = render_to_string('email/order_placed.html', context) 

                    msg = EmailMultiAlternatives(
                        subject = subject,
                        from_email = settings.DEFAULT_FROM_EMAIL,
                        to = [order.email],
                        body = text_body,
                    )

                    msg.attach_alternative(html_body, "text/html")
                    msg.send()

                    return Response({"message": "Payment Successful"})
                
                else:
                    return Response({"message": "Already Paid"})
            #data from stripe API is not "paid" then return message to user 
            elif session.payment_status == "unpaid":
                return Response({"message":"Your Invoice Is Unpaid"})  
            #data from stripe API is "cancelled" then return message to user
            elif session.payment_status == "cancelled":
                return Response({"message":"Your Order Was Cancelled"}) 
            #there was no payment made, so something wrong happen no stripe side API 
            else: 
                return Response ({"message":"An Error Occured, Try Again"})
        #there are no data in response from stripe API it means that there was no payment made
        else: 
            session = None


class ReviewListAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny,]
    queryset = Review.objects.all()

    def get_queryset(self):
        #getting data from request/url data defined in api/url
        product_id = self.kwargs['product_id']
        
        #filter queryset of products to get specific product by its ID
        product = Product.objects.get(id=product_id)
        #find the review for specific product
        reviews = Review.objects.filter(product=product)
        #return review data
        return reviews
    

    def create(self, request, *args, **kwargs):
        #define payload data from reuest data
        payload = request.data
        #catching data from request
        user_id = payload['user_id']
        product_id =payload['product_id']
        rating = payload['rating']
        review = payload['review']

        #using data from request to get User and Product by its IDs
        user = User.objects.get(id=user_id)
        product = Product.objects.get(id=product_id)
        
        #creating Review model instance by using data from payload
        Review.objects.create(
            user = user,
            product = product,
            rating = rating,
            review = review,
        )
        #returnig response message for confirmation that we caught data from frontend and send message success back to frontend
        return Response({"message": "Review Created Successfully"}, status=status.HTTP_201_CREATED)


class SearchPorductAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny,]
    queryset = Product.objects.all()

    def get_queryset(self):
        query = self.request.GET.get("query")
        products = Product.objects.filter(status="published", title__icontains=query)
        return products
        















        
