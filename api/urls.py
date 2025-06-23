from django.urls import path
from userauths import views as userauths_views
from store import views as store_views
from rest_framework_simplejwt.views import TokenRefreshView
from customer import views as customer_views
from vendor import views as vendor_views

urlpatterns = [
    path('user/token/', userauths_views.MyTokenObtainPairView.as_view()),
    path('user/token/refresh/', TokenRefreshView.as_view()),
    path('user/register/', userauths_views.RegisterView.as_view()),
    path('user/password-reset/<email>/', userauths_views.PasswordResetEmailVerify.as_view(), name='password_reset'),
    path('user/password-change/', userauths_views.PasswordChangeView.as_view(), name='password_change' ),
    path('user/profile/<user_id>/', userauths_views.ProfileView.as_view(), name='password_change' ),


    #store endpoints
    path('category/', store_views.CategoryListAPIView.as_view()),
    path('products/', store_views.ProductListAPIView.as_view()),
    path('products/<slug:slug>/', store_views.ProductDetailAPIView.as_view()),
    path('cart-view/', store_views.CartAPIView.as_view()),
    path('cart-list/<str:cart_id>/<int:user_id>/', store_views.CartListView.as_view()),
    path('cart-list/<str:cart_id>/', store_views.CartListView.as_view()),
    path('cart-detail/<str:cart_id>/', store_views.CartDetailView.as_view()),
    path('cart-detail/<str:cart_id>/<int:user_id>/', store_views.CartDetailView.as_view()),
    path('cart-delete/<str:cart_id>/<int:item_id>/<int:user_id>/', store_views.CartItemDeleteAPIView.as_view()),
    path('cart-delete/<str:cart_id>/<int:item_id>/', store_views.CartItemDeleteAPIView.as_view()),
    path('create-order/', store_views.CreateOrderAPIView.as_view()),
    path('checkout/<order_oid>/', store_views.CheckoutView.as_view()),
    path('coupon/', store_views.CouponAPIView.as_view()),
    path('reviews/<product_id>/', store_views.ReviewListAPIView.as_view()),
    path('search/', store_views.SearchPorductAPIView.as_view()),


    # payments endpoints
    path('stripe-checkout/<order_oid>/', store_views.StripeCheckoutView.as_view()),
    path('payment-success/<order_oid>/', store_views.PaymentSuccessView.as_view()),


    #Customer endpoints
    path('customer/orders/<user_id>/', customer_views.OrderAPIView.as_view()),
    path('customer/order/<user_id>/<order_oid>/', customer_views.OrderDetailsAPIView.as_view()),
    path('customer/wishlist/<user_id>/', customer_views.WishlistAPIView.as_view()),
    path('customer/notifications/<user_id>/', customer_views.CustomerNotification.as_view()),
    path('customer/notification/<user_id>/<noti_id>/', customer_views.MarkCustomerNotificationAsSeen.as_view()),

    #Vendor endpoints
    path('vendor/dashboard/<vendor_id>/', vendor_views.DashboardStatsAPIView.as_view()),
    path('vendor/orders-charts/<vendor_id>/', vendor_views.MonthlyOrderChartAPIView),
    path('vendor/products-charts/<vendor_id>/', vendor_views.MonthlyProductChartAPIView),
    path('vendor/products/<vendor_id>/', vendor_views.ProductAPIView.as_view()),
    path('vendor/orders/<vendor_id>/', vendor_views.OrderAPIView.as_view()),
    path('vendor/orders/<vendor_id>/<order_oid>/', vendor_views.OrderdetailAPIView.as_view()),
    path('vendor/filter/orders/<vendor_id>', vendor_views.FilterOrderAPIView.as_view()),
    path('vendor/revenue/<vendor_id>/', vendor_views.RevenueAPIView.as_view()),
    path('vendor/filter-product/<vendor_id>/', vendor_views.FilterProductAPIView.as_view()),
    path('vendor/earnings/<vendor_id>/', vendor_views.EarningAPIView.as_view()),
    path('vendor/monthly-earnings/<vendor_id>/', vendor_views.MonthlyEarningTracker),
    path('vendor/reviews/<vendor_id>/', vendor_views.ReviewListAPIView.as_view()),
    path('vendor/review-details/<vendor_id>/<review_id>/', vendor_views.ReviewDetailAPIView.as_view()),
    path('vendor/coupon-list/<vendor_id>/', vendor_views.CouponListCreateAPIView.as_view()),
    path('vendor/coupon-details/<vendor_id>/<coupon_id>/', vendor_views.CouponDetailsAPIView.as_view()),
    path('vendor/coupon-stats/<vendor_id>/', vendor_views.CouponStatsAPIView.as_view()),
    path('vendor/vendor-noti/<vendor_id>/', vendor_views.NotificationAPIView.as_view()),
    path('vendor/noti-summary/<vendor_id>/', vendor_views.NotificationSummaryAPIView.as_view()),
    path('vendor/noti-mark-as-seen/<vendor_id>/<noti_id>/', vendor_views.NotificationVendorMarkAsSeen.as_view()),
    path('vendor/profile-update/<int:pk>/', vendor_views.VendorProfileUpdateView.as_view()),
    path('vendor/shop-update/<int:pk>/', vendor_views.ShopUpdateView.as_view()),
    path('vendor/shop-view/<vendor_slug>/', vendor_views.ShopAPIView.as_view()),
    path('vendor/products-view/<vendor_slug>/', vendor_views.ShopProductAPIView.as_view()),
    path('vendor/create-product/', vendor_views.ProductCreateView.as_view()),
    path('vendor/update-product/<vendor_id>/<product_pid>/', vendor_views.ProductUpdateAPIView.as_view()),
    path('vendor/delete-product/<vendor_id>/<product_pid>/', vendor_views.ProductDeleteAPIView.as_view()),
    
 
]
