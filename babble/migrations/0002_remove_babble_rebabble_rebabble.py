# Generated by Django 4.1.5 on 2023-03-01 11:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("babble", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="babble",
            name="rebabble",
        ),
        migrations.CreateModel(
            name="Rebabble",
            fields=[
                (
                    "id",
                    models.BigAutoField(primary_key=True, serialize=False, unique=True),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "babble",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="babble.babble"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
