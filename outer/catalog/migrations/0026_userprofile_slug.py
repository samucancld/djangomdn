# Generated by Django 4.0.6 on 2022-07-16 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0025_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='slug',
            field=models.SlugField(default='defaultslug', unique=True),
            preserve_default=False,
        ),
    ]
