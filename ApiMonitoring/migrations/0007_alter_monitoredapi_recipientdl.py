# Generated by Django 5.0.1 on 2024-11-21 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ApiMonitoring', '0006_alter_monitoredapi_recipientdl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitoredapi',
            name='recipientDl',
            field=models.JSONField(),
        ),
    ]
