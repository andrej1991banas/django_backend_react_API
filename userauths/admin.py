from django.contrib import admin
from .models import User,Profile




class UserAdmin(admin.ModelAdmin):
    list_display = ['id','username', 'fullname', 'email', 'mobile', ]
    search_fields = ['username', 'email', ]

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['pid','fullname', 'gender', 'country', ]
    list_filter = ['gender', 'country', ]



admin.site.register(User,UserAdmin )
admin.site.register(Profile, ProfileAdmin)


