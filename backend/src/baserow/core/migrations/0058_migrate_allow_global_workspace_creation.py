# Generated by Django 3.2.13 on 2023-02-13 10:32

from django.db import migrations, models


def forward(apps, schema_editor):
    Settings = apps.get_model("core", "Settings")

    Settings.objects.update(
        allow_global_workspace_creation=models.F("allow_global_group_creation")
    )


def backward(apps, schema_editor):
    Settings = apps.get_model("core", "Settings")

    Settings.objects.update(
        allow_global_group_creation=models.F("allow_global_workspace_creation")
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0057_settings_allow_global_workspace_creation"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
