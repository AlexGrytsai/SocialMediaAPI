# Generated by Django 5.0.7 on 2024-08-06 08:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("users", "0013_remove_user_check_age_user_check_age"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="user",
            name="check_age",
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("birth_date__isnull", True),
                    models.Q(
                        ("birth_date__lte", datetime.date(2011, 8, 10)),
                        ("birth_date__gte", datetime.date(1924, 8, 31)),
                    ),
                    _connector="OR",
                ),
                name="check_age",
                violation_error_message="User must be at least 13 years old and less than 100 years old.",
            ),
        ),
    ]
