# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0005_auto_20150217_0056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='constituent',
            name='zipCode',
            field=models.CharField(max_length=5, validators=[django.core.validators.RegexValidator('^.....$', message='Zip codes are five digits only.'), django.core.validators.RegexValidator('^[0-9][0-9][0-9][0-9][0-9]$', message='Zip codes are five digits only.')], db_column='zip_code'),
            preserve_default=True,
        ),
    ]
