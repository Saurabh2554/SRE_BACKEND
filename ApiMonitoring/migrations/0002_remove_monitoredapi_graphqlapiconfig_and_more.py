# Generated by Django 5.0.1 on 2025-02-24 09:41

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ApiMonitoring', '0001_initial'),
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
        migrations.RemoveField(
            model_name='monitoredapi',
            name='apiCallInterval',
        ),
        migrations.RemoveField(
            model_name='monitoredapi',
            name='apiType',
        ),
        migrations.RemoveField(
            model_name='monitoredapi',
            name='createdBy',
        ),
        migrations.RemoveField(
            model_name='monitoredapi',
            name='expectedResponseTime',
        ),
        migrations.RemoveField(
            model_name='monitoredapi',
            name='recipientDl',
        ),
        migrations.AddField(
            model_name='apimetrics',
            name='degraded',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='apimetrics',
            name='failed',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='monitoredapi',
            name='degradedResponseTime',
            field=models.IntegerField(blank=True, help_text='Threshold in milliseconds', null=True),
        ),
        migrations.AddField(
            model_name='monitoredapi',
            name='failedResponseTime',
            field=models.IntegerField(blank=True, help_text='Threshold in milliseconds', null=True),
        ),
        migrations.AddField(
            model_name='monitoredapi',
            name='methodType',
            field=models.CharField(choices=[('GET', 'GET'), ('POST', 'POST')], default='GET', max_length=10),
        ),
        migrations.AddField(
            model_name='monitoredapi',
            name='requestBody',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='apimetrics',
            name='responseSize',
            field=models.IntegerField(blank=True, default=233, null=True),
        ),
        migrations.CreateModel(
            name='AssertionAndLimit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('source', models.CharField(blank=True, choices=[('status_code', 'Status Code'), ('headers', 'Headers'), ('json_body', 'JSON Body')], max_length=50, null=True)),
                ('property', models.CharField(blank=True, max_length=255, null=True)),
                ('operator', models.CharField(blank=True, choices=[('equals', 'Equals'), ('not_equals', 'Not Equals'), ('greater_than', 'Greater Than'), ('less_than', 'Less Than'), ('contains', 'Contains')], max_length=20, null=True)),
                ('expectedValue', models.CharField(blank=True, max_length=255, null=True)),
                ('api', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assertionAndLimit', to='ApiMonitoring.monitoredapi')),
            ],
        ),
        migrations.CreateModel(
            name='AssertionAndLimitResult',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('actual_value', models.TextField(null=True)),
                ('status', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('apimetrics', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ApiMonitoring.apimetrics')),
                ('assertion_and_limit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ApiMonitoring.assertionandlimit')),
            ],
        ),
        migrations.CreateModel(
            name='SchedulingAndAlerting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('apiCallInterval', models.IntegerField(blank=True, default=5, null=True)),
                ('maxRetries', models.IntegerField(blank=True, default=3, null=True)),
                ('retryAfter', models.IntegerField(blank=True, default=60, null=True)),
                ('recipientDl', models.JSONField()),
                ('createdBy', models.EmailField(blank=True, max_length=254, null=True)),
                ('teamsChannelWebhookURL', models.TextField(blank=True, default='https://azureinfogroup.webhook.office.com/webhookb2/4bdeb1f8-9ed8-400f-8dd5-9db44aa4e0fc@843d9d80-d651-4366-8ce8-7a742772332b/IncomingWebhook/b91716c5da624076a0528c2b73f8201e/5bf898a4-9715-4c6e-92c8-245097d00e9c/V2pT5l0z6zrFYc7aBMqSplOv-TYsRavwkhXaeHD0Nb8Uc1', null=True)),
                ('api', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedulingAndAlerting', to='ApiMonitoring.monitoredapi')),
            ],
        ),
        migrations.DeleteModel(
            name='GraphQLAPIConfig',
        ),
        migrations.DeleteModel(
            name='RestAPIConfig',
        ),
    ]
