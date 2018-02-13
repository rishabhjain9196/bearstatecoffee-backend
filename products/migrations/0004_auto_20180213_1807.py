# Generated by Django 2.0.2 on 2018-02-13 12:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0003_auto_20180213_1604'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_number', models.IntegerField()),
                ('period_name', models.CharField(max_length=100)),
                ('terms', models.CharField(max_length=5000)),
            ],
        ),
        migrations.CreateModel(
            name='Subscriptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('status', models.CharField(choices=[('A', 'ACTIVE'), ('P', 'PAUSED'), ('C', 'CANCELLED'), ('F', 'FINISHED')], default='A', max_length=1)),
                ('next_order_date', models.DateTimeField()),
                ('last_order_date', models.DateTimeField()),
                ('category_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Categories')),
            ],
        ),
        migrations.AlterField(
            model_name='cartproducts',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='orders',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='products',
            name='category_ids',
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='order_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Orders'),
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Products'),
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='products',
            name='category_ids',
            field=models.ManyToManyField(to='products.Categories'),
        ),
    ]
