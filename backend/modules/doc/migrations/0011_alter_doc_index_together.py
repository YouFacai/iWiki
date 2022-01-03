# Generated by Django 4.0 on 2022-01-01 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("doc", "0010_doc_update_by_docversion_update_by"),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name="doc",
            index_together={
                ("repo_id", "creator"),
                ("update_at", "is_deleted", "available"),
                ("creator", "is_deleted"),
            },
        ),
    ]