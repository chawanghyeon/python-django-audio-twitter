# Generated by Django 4.1.5 on 2023-01-09 04:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Babble",
            fields=[
                (
                    "id",
                    models.IntegerField(primary_key=True, serialize=False, unique=True),
                ),
                ("audio", models.FileField(upload_to="audio/%Y/%m/%d")),
                ("duration", models.IntegerField(blank=True, null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True, null=True)),
                (
                    "reBable",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="babble.babble",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("text", models.CharField(max_length=20)),
                ("crated", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.IntegerField(primary_key=True, serialize=False, unique=True),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("password", models.CharField(max_length=20)),
                ("first_name", models.CharField(max_length=20)),
                ("last_name", models.CharField(max_length=20)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True, null=True)),
                ("birthday", models.DateTimeField(blank=True, null=True)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="image/%Y/%m/%d"
                    ),
                ),
                (
                    "background",
                    models.ImageField(
                        blank=True, null=True, upload_to="image/%Y/%m/%d"
                    ),
                ),
                ("nickname", models.CharField(blank=True, max_length=20, unique=True)),
                ("location", models.CharField(blank=True, max_length=20)),
                ("phoneNumber", models.CharField(blank=True, max_length=20)),
                ("gender", models.CharField(blank=True, max_length=20)),
                ("bio", models.CharField(blank=True, max_length=140)),
            ],
        ),
        migrations.CreateModel(
            name="Like",
            fields=[
                (
                    "id",
                    models.IntegerField(primary_key=True, serialize=False, unique=True),
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
                        on_delete=django.db.models.deletion.CASCADE, to="babble.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Follower",
            fields=[
                (
                    "id",
                    models.IntegerField(primary_key=True, serialize=False, unique=True),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "following",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="following",
                        to="babble.user",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="babble.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.IntegerField(primary_key=True, serialize=False, unique=True),
                ),
                ("audio", models.FileField(upload_to="audio/%Y/%m/%d")),
                ("duration", models.IntegerField(blank=True, null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True, null=True)),
                (
                    "babble",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="babble.babble"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="babble.user"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="babble",
            name="tags",
            field=models.ManyToManyField(blank=True, to="babble.tag"),
        ),
        migrations.AddField(
            model_name="babble",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="babble.user"
            ),
        ),
    ]
