# Generated by Django 5.0.1 on 2024-12-05 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ApiMonitoring', '0007_alter_monitoredapi_recipientdl'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitoredapi',
            name='teamsChannelWebhookURL',
            field=models.TextField(default='https://azureinfogroup.webhook.office.com/webhookb2/4bdeb1f8-9ed8-400f-8dd5-9db44aa4e0fc@843d9d80-d651-4366-8ce8-7a742772332b/IncomingWebhook/b91716c5da624076a0528c2b73f8201e/5bf898a4-9715-4c6e-92c8-245097d00e9c/V2pT5l0z6zrFYc7aBMqSplOv-TYsRavwkhXaeHD0Nb8Uc1'),
        ),
    ]
