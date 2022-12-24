# Generated by Django 4.1.4 on 2022-12-24 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Babble",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("fileUrl", models.CharField(max_length=140)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("password", models.CharField(max_length=20)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("avatar", models.CharField(max_length=140)),
                ("background", models.CharField(max_length=140)),
                ("nickname", models.CharField(max_length=20)),
                ("location", models.CharField(max_length=20)),
                ("phoneNumber", models.CharField(max_length=20)),
                ("gender", models.CharField(max_length=20)),
                ("bio", models.CharField(max_length=140)),
                ("birthday", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("text", models.CharField(max_length=20)),
                ("crated", models.DateTimeField(auto_now_add=True)),
                (
                    "babble",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="babble.babble"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ReBabble",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("fileUrl", models.CharField(max_length=140)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "babble",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="babble.babble",
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
            name="Like",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
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
                ("id", models.IntegerField(primary_key=True, serialize=False)),
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
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("fileUrl", models.CharField(max_length=140)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
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
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="babble.user"
            ),
        ),
    ]
