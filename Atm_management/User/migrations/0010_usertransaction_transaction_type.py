# Generated by Django 5.0.7 on 2024-07-31 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0009_remove_customuser_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertransaction',
            name='transaction_type',
            field=models.CharField(default='Blank', max_length=50),
        ),
    ]