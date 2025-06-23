from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from shortuuid.django_fields import ShortUUIDField



class User(AbstractUser):
    #defyning the CustomUser model
    username = models.CharField(max_length=100)
    email=models.EmailField(max_length=100, unique=True)
    fullname = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    otp = models.CharField(max_length=100, null=True, blank=True)

    # Overwrite the username from User model to be an email in our Custom user
    #it is for authentication phase
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        email_username, mobile = self.email.split("@")
        #as the full_name is not required we will define function to get some from email
        if self.fullname=="" or self.fullname == None:
            self.fullname = email_username #rewrite empty full_name with an first part of the email
        if self.username=="" or self.username == None:
            self.username = email_username #username not in authentication part will be set as a first part of the email

        super(User,self).save(*args,**kwargs)



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #data fom Custom User model, chain with Profile model data
    image = models.FileField(default='default/default-user.jpg', upload_to="iamge", null=True, blank=True)
    fullname = models.CharField(max_length=100, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    pid = ShortUUIDField(primary_key=True, length=10, max_length=20, alphabet="abcdefghijkmnoprstquvwxz123456789!@#$%^&*()")


    def __str__(self):
        if self.fullname:
            return str(self.fullname)
        else:
            str(self.user.fullname)


    def save(self, *args, **kwargs):
        if self.fullname=="" or self.fullname == None:
            self.fullname = self.user.fullname #rewrite empty full_name with an first part of the email


        super(Profile,self).save(*args,**kwargs)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)





