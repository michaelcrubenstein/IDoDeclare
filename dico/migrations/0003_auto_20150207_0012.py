# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0002_auto_20150206_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='constituent',
            name='zipCode',
            field=models.IntegerField(db_column='zip_code', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(99999)]),
            preserve_default=True,
        ),
    ]
