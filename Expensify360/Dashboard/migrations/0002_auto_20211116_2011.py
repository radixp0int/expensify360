# Generated by Django 3.1.13 on 2021-11-16 20:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'permissions': [('can_create', 'Can Create Organizations')]},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'permissions': [('can_create', 'Can Create Projects'), ('can_manage', 'Can Manage Users')]},
        ),
    ]
