# Generated by Django 5.0.7 on 2024-07-29 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_user_birth_date_alter_user_followers_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                blank=True, max_length=150, null=True, verbose_name="username"
            ),
        ),
    ]
