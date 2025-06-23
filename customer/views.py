from django.shortcuts import render, redirect
from django.conf import settings
from userauths.models import User
from store.models import Product, Category, Gallery, Specification, Size, Color, Cart, CartOrder, CartOrderItem, Coupons, Wishlist, Review, ProductFaq, Notification,Tax
from store.serializers import ProductFaqSerializer, CategorySerializer,WishlistSerializer, ProductSerializer, CartSerializer, CartOrderSerializer, CartOrderItemSerializer,CouponsSerializer, NotificationSerializer, ReviewSerializer

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from decimal import Decimal
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class OrderAPIView(generics.ListAPIView):
    """ API view with orders filter by logged in user and payment status 'paid' """
    permission_classes = [AllowAny] #for production change to IsAuthenticated
    serializer_class = CartOrderSerializer

    #redefine get_queryset method
    def get_queryset(self):
        #get uset from request data
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        #filter order according to user_id and paid status
        orders = CartOrder.objects.filter(buyer=user, payment_status='paid')
        return orders
    


class OrderDetailsAPIView(generics.RetrieveAPIView):
    """ API view for order details"""
    permission_classes = [AllowAny]
    serializer_class = CartOrderSerializer
    #get data fromm request data with user and order_oid
    def get_object(self):
        user_id = self.kwargs['user_id']
        order_oid = self.kwargs['order_oid']

        user = User.objects.get(id=user_id) 
        order = CartOrder.objects.get(buyer=user, oid=order_oid, payment_status="paid")

        return order


class WishlistAPIView(generics.ListCreateAPIView):
    """ Usinf ListCreateAPIView for GET and POST request, getting wishlists for user and creating new ones"""
    serializer_class = WishlistSerializer
    permission_classes = [AllowAny,]

    def get_queryset(self):
        #get data of existed wishlists for logged in user 
        user_id = self.kwargs['user_id']

        user = User.objects.get(id=user_id)

        wishlists = Wishlist.objects.filter(user=user)
        return wishlists
    
    def create(self, request, *args, **kwargs):
        payload = request.data
        #use payload data for creating new wishlist assigned to logged in user 
        product_id = payload['product_id']
        user_id = payload ['user_id']

        product = Product.objects.get(id=product_id)
        user = User.objects.get(id=user_id)

        wishlist = Wishlist.objects.filter(product=product, user=user)
        if wishlist:
            wishlist.delete()
            return Response ({"message": "Wishlist Deleted Successfuly"}, status=status.HTTP_200_OK)
        else:
            Wishlist.objects.create(product=product, user=user)
            return Response({"message":"WishlistCreted Successfully"}, status=status.HTTP_201_CREATED)


class CustomerNotification(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny,]    


    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        notifications = Notification.objects.filter(user=user, seen=False)
        return notifications

class MarkCustomerNotificationAsSeen(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny,]


    def get_object(self):
        user_id = self.kwargs['user_id']
        noti_id = self.kwargs['noti_id']
        user = User.objects.get(id=user_id)
        noti = Notification.objects.get(id=noti_id)

        if noti.seen!= True:

            noti.seen = True
            noti.save()
        return noti





