# Generated by Django 5.0.7 on 2024-07-29 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="user",
            name="users_user_usernam_1d8d1d_idx",
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["username"], name="users_user_usernam_65d164_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["last_name", "first_name"],
                name="users_user_last_na_be362d_idx",
            ),
        ),
    ]
