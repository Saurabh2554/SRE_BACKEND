# Generated by Django 5.0.1 on 2024-01-19 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0002_alter_businessunit_id_alter_subbusinessunit_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subbusinessunit',
            old_name='businessUnitId',
            new_name='businessUnit',
        ),
    ]