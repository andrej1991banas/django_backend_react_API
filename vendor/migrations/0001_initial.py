# Generated by Django 4.2 on 2025-05-28 10:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(blank=True, default='vendor.jpg', null=True, upload_to='vendor')),
                ('name', models.CharField(blank=True, help_text='Shop Name', max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('mobile', models.CharField(blank=True, help_text='Shop Phone Number', max_length=100, null=True)),
                ('active', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(max_length=500, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Vendors',
                'ordering': ['-date'],
            },
        ),
    ]
