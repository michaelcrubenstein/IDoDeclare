# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('dico', '0001_initial'),
        ('custom_user', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='constituent',
            name='email',
        ),
        migrations.RemoveField(
            model_name='constituent',
            name='firstName',
        ),
        migrations.RemoveField(
            model_name='constituent',
            name='lastName',
        ),
        migrations.RemoveField(
            model_name='mc',
            name='email',
        ),
        migrations.RemoveField(
            model_name='mc',
            name='firstName',
        ),
        migrations.RemoveField(
            model_name='mc',
            name='lastName',
        ),
        migrations.AddField(
            model_name='constituent',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mc',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id', default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='constituent',
            name='zipCode',
            field=models.IntegerField(validators=[django.core.validators.RegexValidator('^[0-9][0-9][0-9][0-9][0-9]$', message='Zip codes are five digits only.')], db_column='zip_code'),
            preserve_default=True,
        ),
    ]
