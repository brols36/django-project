# Generated by Django 5.0.7 on 2024-08-06 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0020_remove_usertransaction_check_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='open_balance',
            field=models.IntegerField(default=0),
        ),
    ]
