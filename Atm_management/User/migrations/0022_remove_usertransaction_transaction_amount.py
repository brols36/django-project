# Generated by Django 5.0.7 on 2024-08-06 07:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0021_customuser_open_balance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertransaction',
            name='transaction_amount',
        ),
    ]
