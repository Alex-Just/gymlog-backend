# Generated by Django 4.2.14 on 2024-07-23 13:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gym", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="exercise",
            name="name_en",
            field=models.CharField(max_length=255, null=True, verbose_name="Name"),
        ),
        migrations.AddField(
            model_name="exercise",
            name="name_es",
            field=models.CharField(max_length=255, null=True, verbose_name="Name"),
        ),
        migrations.AddField(
            model_name="exercise",
            name="name_ru",
            field=models.CharField(max_length=255, null=True, verbose_name="Name"),
        ),
    ]