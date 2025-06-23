from django.db import models
from vendor.models import Vendor
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save
from userauths.models import User, Profile


from shortuuid.django_fields import ShortUUIDField



# Create your models here.
class Category(models.Model):
    #name of the Category
    title = models.CharField(max_length=100)
    #Category image
    image = models.FileField(upload_to="category_images/", default="category.jpg", null=True, blank=True)
    #status of the Category
    atcive = models.BooleanField(default=True)
    #title with "-" mark inbetween words
    slug = models.SlugField(unique=True)

    #string representaion of the model
    def __str__(self):
        return self.title
    
        #defining plurals state of the model and ordering
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['title']



class Product(models.Model):
    #choices to set status of the product
    STATUS = (
        ("draft", "Drafted"),
        ("disabled", "Disabled"),
        ("in_review", "In Review"),
        ("published", "Published"),
    )
    #name of the Product item
    title = models.CharField(max_length=100)
    #prpduct image
    image = models.FileField(upload_to="product_images/", default="product.jpg", null=True, blank=True)
    #description for the product
    description = models.TextField(null= True, blank=True)
    #reference for the Product model to the Category model
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    #number representing the price of the Product item
    price = models.DecimalField(decimal_places=2, max_digits=12)
    #historical changes kept here
    old_price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    shipping_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    #stock of the product on the store, default 1, as for 0 there is in_stock status False
    stock_qty = models.PositiveIntegerField(default=1)
    in_stock = models.BooleanField(default=True)
    #status of the product according to choices and its status in process to get it into store stocks and sales
    status = models.CharField(max_length=100, choices=STATUS, default="published")
    featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    #rating of the product, calculated by the Review model
    rating = models.PositiveIntegerField(default=0)
    #reference to the Vendor model that created the product
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    #unique id for the product,created from characters in "alphabet"
    pid = ShortUUIDField(unique=True, length=10, alphabet="acbfsgeiohvpa123456")
    #title with "-" mark inbetween words
    slug = models.SlugField(null=True, blank=True)
    #date of creation
    date = models.DateTimeField(auto_now_add=True)

     #defining plurals state of the model and ordering
    class Meta:
        verbose_name_plural = "Products"
        ordering = ['-date']

    
    #string representaion of the model
    def __str__(self):
        return self.title
    

    #getting Rating for product funciton
    def product_rating(self):
        product_rating = Review.objects.filter(product=self).aggregate(avg_rating=models.Avg('rating')) #populate avg_rating with the average of all ratings for this product
        return product_rating['avg_rating']

    #getting product_rating variable from product_rating function and populating rating field in Product model, saving it to the db
    def save(self, *args, **kwargs):
        self.rating = self.product_rating() #calling the product rating function, getting rating and saving to the moedel Product.rating
        super(Product, self).save(*args, **kwargs)

    #functions for the ProductSerializer
    #defining count for rating fucntion
    def rating_count(self):
        rating_count = Review.objects.filter(product=self).count()
        return rating_count

    #gallery function to get all images for the product from the gallery model
    def gallery(self):
        gallery = Gallery.objects.filter(product=self)
        return gallery
    
    #funciton to get Specification model data to the Product data
    def specification(self):
        return Specification.objects.filter(product=self)
    
    def size(self):
        return Size.objects.filter(product=self)
    
    def color(self):
        return Color.objects.filter(product=self)


   #save funciton to populate slug field and saving product item into db
    def save(self, *args, **kwargs):
        if self.slug =="" or self.slug == None: #we do not provide slug, so we create it
            self.slug = slugify(self.title)
        super(Product, self).save(*args, **kwargs) #creating and populating slug, if not provided

    


    
# Model for Product Gallery
class Gallery(models.Model):
    #reference to the Product model
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    #images upploaded to the same directory as Product images, it is the same imagaes too
    image = models.FileField(upload_to="product_images/", default="product.jpg", null=True, blank=True)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    #unique id for the gallery,,created from characters in "alphabet"
    gid = ShortUUIDField(unique=True, length=10, alphabet="acbfsgeiohvpa123456")

    class Meta:
        verbose_name_plural = "Product Images"

    #string representaion of the model
    def __str__(self):
        return self.product.title
    


# Model for Product Specifications
class Specification(models.Model):
    #reference to the Product model
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=1000, null=True, blank=True)
    content = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title   
    


# Model for Product Sizes
class Size(models.Model):
      #reference to the Product model
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    #name of the size
    name = models.CharField(max_length=1000, null=True, blank=True)
    #price for different size
    price = models.DecimalField(decimal_places=2, max_digits=12)
    date = models.DateTimeField(auto_now_add=True)

    #string representation of the Size model
    def __str__(self):
        return self.name   
    



# Model for Product Colors
class Color(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=1000, null=True, blank=True)
    color_code = models.CharField(max_length=1000, null=True, blank=True)

    #string representation of the Color model
    def __str__(self):
        return self.name 
    

# Model for Cart
class Cart(models.Model):
    #reference to the Product model
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    #reference to the User model
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    #quantity in Cart
    qty = models.PositiveIntegerField(default=1)
    #price of the items in cart
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    #total price of the items in cart qty*price
    sub_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    shipping_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    service_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    tax_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    #sum of the all price sections in the Model
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    country = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    cart_id = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.cart_id} - {self.product.title}"


# Model for Cart Orders
class CartOrder(models.Model):
    PAYMENT_STATUS = (
            ("paid", "Paid"),
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("cancelled", "Caneclled"),
        )
    
    ORDER_STATUS = (
            ("paid", "Paid"),
            ("pending", "Pending"),
            ("fullflled", "Fullfilled"),
            ("cancelled", "Caneclled"),
        )
    #reference to Vendor model
    vendor = models.ManyToManyField(Vendor, blank=True)
    #reference to User model
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
     # Total price of the order
    sub_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    shipping_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    service_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    tax_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    #sum of the all price section within the model 
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

    # Order status attributes
    payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=100, default="pending")
    order_status = models.CharField(choices=ORDER_STATUS, max_length=100, default="pending")

    #Discounts
    initial_total = models.DecimalField(default =0.00, max_digits=12, decimal_places=2)
    saved = models.DecimalField(default =0.00, max_digits=12, decimal_places=2)

    #Personal Informations
    full_name = models.CharField(max_length=100, null=True, blank=True) 
    email = models.CharField(max_length=100, null=True, blank=True) 
    mobile = models.CharField(max_length=100, null=True, blank=True) 

    #shipping address
    address = models.CharField(max_length=100, null=True, blank=True) 
    city = models.CharField(max_length=100, null=True, blank=True) 
    state = models.CharField(max_length=100, null=True, blank=True) 
    country = models.CharField(max_length=100, null=True, blank=True) 

    stripe_session_id = models.CharField(max_length=1000, null=True, blank=True)

    oid = ShortUUIDField(unique=True, length=10, alphabet="acbfsgeiohvpa123456")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.oid
    
    def orderitem(self):
        return CartOrderItem.objects.filter(order=self)


# Define a model for Cart Order Item
class CartOrderItem(models.Model):
     # A foreign key relationship to the CartOrder model with CASCADE deletion
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE, related_name="orderitem")
    # A foreign key relationship to the Product model with CASCADE deletion
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_item")
    # Integer field to store the quantity (default is 0)
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    sub_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    shipping_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    service_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    tax_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    country = models.CharField(max_length=100, null=True, blank=True)
     # Fields for color and size with max length 100, allowing null and blank values
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)

    #Coupons
    coupon = models.ManyToManyField("store.Coupons", blank=True)
    initial_total = models.DecimalField(default =0.00, max_digits=12, decimal_places=2)
    saved = models.DecimalField(default =0.00, max_digits=12, decimal_places=2)

    oid = ShortUUIDField(unique=True, length=10, alphabet="acbfsgeiohvpa123456")
    date = models.DateTimeField(auto_now_add=True)

    # A foreign key relationship to the Vendor model with SET_NULL option
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
   
        
    def __str__(self):
        return self.oid


class ProductFaq(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)    
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000, null=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product FAQs"


# Define a model for Reviews
class Review(models.Model):
    #choose panel for Rating options
    RATING = (
            (1,"1 Star"),
            (2,"2  Stars"),
            (3,"3  Stars"),
            (4,"4 Stars"),
            (5,"5  Stars"),
        )
    #reference to User model
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    #reference to Product model
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    #actual review and reply
    review = models.TextField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)
    #choose option for rating the Product
    rating = models.IntegerField (default=None, choices=RATING)
    # Boolean field for the active status of the Review
    active = models.BooleanField(default=False)
    #date of creation
    date = models.DateTimeField(auto_now_add=True)  

    
    class Meta:
        verbose_name_plural = "Reviews & Rating"


    def profile(self):
        return Profile.objects.get(user=self.user)
    
    #string representation of the Review model  
    def __str__(self):
        return self.product.title


#signal that will run everytime that the new Review model is created
@receiver(post_save, sender=Review)
def update_product_rating(sender, instance, **kwargs):
    if instance.product:
        instance.product.save()


# Define a model for Wishlist
class Wishlist(models.Model):
    # A foreign key relationship to the User model with CASCADE deletion
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # A foreign key relationship to the Product model with CASCADE deletion, specifying a related name
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist")
    # Date and time field
    date = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return self.product.title



class Notification(models.Model):
    #reference to User model
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    #reference to the CartOrder model
    order = models.ForeignKey(CartOrder, on_delete=models.SET_NULL, null=True, blank=True)  
    #reference to the Vendor model
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    #reference to the CartOrderItem model
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

      # Method to return a string representation of the object
    def __str__(self):
        if self.order:
            return self.order.oid
        else:
            return f"Nofication - {self.pk}"



class Coupons(models.Model):
    # A foreign key relationship to the Vendor model with SET_NULL option, allowing null values, and specifying a related name
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="coupon_vendor")
    # Many-to-many relationship with User model for users who used the coupon
    used_by = models.ManyToManyField(User, blank=True)
    # Fields for code, type, discount, redemption, date, and more
    code = models.CharField(max_length=1000)
    # type = models.CharField(max_length=100, choices=DISCOUNT_TYPE, default="Percentage")
    discount = models.IntegerField(default=1)
    # redemption = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    # Method to return a string representation of the object
    def __str__(self):
        return self.code
   


class Tax(models.Model):
    country = models.CharField(max_length=100)
    rate = models.IntegerField(default=23, help_text="Numbers added ere are in percentage e.g.23%")
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return self.country
    class Meta:
        verbose_name_plural = "Taxes"
        ordering = ['country']
