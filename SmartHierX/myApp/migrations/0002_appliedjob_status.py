# Generated by Django 5.1.6 on 2025-04-07 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appliedjob',
            name='status',
            field=models.CharField(blank=True, choices=[('Accepted', 'Accepted'), ('Declined', 'Declined')], max_length=20, null=True),
        ),
    ]
