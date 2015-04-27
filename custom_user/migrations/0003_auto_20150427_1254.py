# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0002_passwordreset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authuser',
            name='email',
            field=models.EmailField(max_length=255, verbose_name='email address', db_index=True, unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='passwordreset',
            name='email',
            field=models.EmailField(max_length=255, verbose_name='email address', db_index=True, unique=True),
            preserve_default=True,
        ),
    ]
