# Generated by Django 5.0.1 on 2024-11-19 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ApiMonitoring', '0003_remove_monitoredapi_apitype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monitoredapi',
            name='graphqlApiconfig',
        ),
        migrations.RemoveField(
            model_name='monitoredapi',
            name='restApiConfig',
        ),
        migrations.AlterField(
            model_name='monitoredapi',
            name='methodType',
            field=models.CharField(choices=[('GET', 'GET'), ('POST', 'POST')], max_length=10),
        ),
    ]
