# Generated by Django 5.0.7 on 2024-08-05 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0019_usertransaction_check_balance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertransaction',
            name='check_balance',
        ),
    ]
