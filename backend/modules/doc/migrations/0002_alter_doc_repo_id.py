# Generated by Django 3.2.9 on 2021-11-30 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("doc", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="doc",
            name="repo_id",
            field=models.BigIntegerField(db_index=True, verbose_name="仓库id"),
        ),
    ]
