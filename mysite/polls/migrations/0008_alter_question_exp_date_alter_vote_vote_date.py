# Generated by Django 4.2.7 on 2023-11-06 11:33

import datetime
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_remove_vote_future_date_not_allowed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='exp_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 13, 11, 33, 43, 840487), verbose_name='expiration date'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='vote_date',
            field=models.DateTimeField(default=django.utils.timezone.now, validators=[django.core.validators.MaxValueValidator(limit_value=django.utils.timezone.now)]),
        ),
    ]
