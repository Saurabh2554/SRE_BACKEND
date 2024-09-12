# Generated by Django 5.0.1 on 2024-09-12 14:01

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ApiMonitoring', '0005_remove_restapimetrics_response_payload'),
        ('Business', '0003_rename_businessunitid_subbusinessunit_businessunit'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonitoredAPI',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('apiName', models.CharField(max_length=255)),
                ('apiType', models.CharField(choices=[('REST', 'REST API'), ('GraphQL', 'GraphQL API')], max_length=50)),
                ('apiUrl', models.URLField()),
                ('apiCallInterval', models.IntegerField(default=5)),
                ('expectedResponseTime', models.IntegerField(default=10)),
                ('headers', models.JSONField(blank=True, null=True)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('recipientDl', models.EmailField(max_length=254)),
                ('createdBy', models.EmailField(blank=True, max_length=254)),
                ('authentication', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ApiMonitoring.authentication')),
                ('businessUnit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Business.businessunit')),
                ('graphqlApiconfig', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ApiMonitoring.graphqlapiconfig')),
                ('restApiConfig', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ApiMonitoring.restapiconfig')),
                ('subBusinessUnit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Business.subbusinessunit')),
            ],
        ),
    ]
