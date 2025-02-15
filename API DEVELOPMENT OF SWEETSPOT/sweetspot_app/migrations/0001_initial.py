# Generated by Django 5.1.2 on 2024-10-24 14:09

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('flavour', models.CharField(max_length=100)),
                ('size', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, upload_to='cakes/')),
                ('available', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('phone_no', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('pincode', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='CakeCustomization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(blank=True, max_length=200)),
                ('egg_version', models.BooleanField(default=True)),
                ('toppings', models.CharField(blank=True, max_length=200)),
                ('shape', models.CharField(default='round', max_length=50)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('cake', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetspot_app.cake')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sweetspot_app.customer')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('cake', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetspot_app.cake')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='sweetspot_app.cart')),
                ('customization', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sweetspot_app.cakecustomization')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetspot_app.customer'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('order_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('delivery_address', models.TextField()),
                ('order_status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('payment_method', models.CharField(choices=[('cod', 'Cash on Delivery'), ('card', 'Card')], default='cod', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('card_number', models.CharField(blank=True, max_length=16, null=True)),
                ('card_holder_name', models.CharField(blank=True, max_length=100, null=True)),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('cvv', models.CharField(blank=True, max_length=3, null=True)),
                ('cake_customization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sweetspot_app.cakecustomization')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetspot_app.customer')),
                ('items', models.ManyToManyField(to='sweetspot_app.cake')),
            ],
        ),
    ]
