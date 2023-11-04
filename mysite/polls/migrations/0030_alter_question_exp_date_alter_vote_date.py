# Generated by Django 4.2.7 on 2023-11-04 18:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0029_alter_question_exp_date_alter_vote_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='exp_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 11, 18, 14, 32, 125330), verbose_name='expiration date'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 4, 18, 14, 32, 190333)),
        ),
    ]
