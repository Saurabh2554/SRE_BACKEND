# Generated by Django 5.0.1 on 2024-10-18 10:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ApiMonitoring', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monitoredapi',
            name='taskId',
        ),
    ]
