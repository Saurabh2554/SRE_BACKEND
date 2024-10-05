# Generated by Django 5.0.1 on 2024-10-05 12:13

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Business', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Authentication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_type', models.CharField(choices=[('NONE', 'No Authentication'), ('API_KEY', 'API Key'), ('BASIC', 'Basic Authentication'), ('BEARER', 'Bearer Token (OAuth)'), ('CUSTOM', 'Custom Authentication')], default='NONE', max_length=50)),
                ('api_key', models.CharField(blank=True, max_length=255, null=True)),
                ('basic_username', models.CharField(blank=True, max_length=255, null=True)),
                ('basic_password', models.CharField(blank=True, max_length=254, null=True)),
                ('bearer_token', models.TextField(blank=True, null=True)),
                ('custom_auth_headers', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GraphQLAPIConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graphql_query', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='RestAPIConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(default='GET', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='MonitoredAPI',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('apiName', models.CharField(blank=True, max_length=255, null=True)),
                ('apiType', models.CharField(choices=[('REST', 'REST API'), ('GraphQL', 'GraphQL API')], max_length=50)),
                ('apiUrl', models.URLField()),
                ('apiCallInterval', models.IntegerField(blank=True, default=5, null=True)),
                ('expectedResponseTime', models.IntegerField(blank=True, default=10, null=True)),
                ('headers', models.JSONField(blank=True, null=True)),
                ('isApiActive', models.BooleanField(default=False)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('recipientDl', models.EmailField(max_length=254)),
                ('createdBy', models.EmailField(blank=True, max_length=254, null=True)),
                ('businessUnit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Business.businessunit')),
                ('graphqlApiconfig', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ApiMonitoring.graphqlapiconfig')),
                ('subBusinessUnit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Business.subbusinessunit')),
                ('restApiConfig', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ApiMonitoring.restapiconfig')),
            ],
        ),
        migrations.CreateModel(
            name='APIMetrics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('requestStartTime', models.DateTimeField(default=django.utils.timezone.now)),
                ('firstByteTime', models.DateTimeField(default=django.utils.timezone.now)),
                ('responseTime', models.FloatField(blank=True, null=True)),
                ('success', models.BooleanField(default=False)),
                ('errorMessage', models.TextField(blank=True, null=True)),
                ('statusCode', models.IntegerField(blank=True, null=True)),
                ('responseSize', models.IntegerField(default=233)),
                ('api', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='ApiMonitoring.monitoredapi')),
            ],
        ),
    ]