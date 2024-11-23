# Generated by Django 5.0.1 on 2024-11-15 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ApiMonitoring', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitoredapi',
            name='methodType',
            field=models.CharField(default='GET', max_length=10),
        ),
        migrations.AddField(
            model_name='monitoredapi',
            name='requestBody',
            field=models.TextField(blank=True, null=True),
        ),
    ]