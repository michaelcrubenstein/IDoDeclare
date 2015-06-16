# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0003_auto_20150427_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authuser',
            name='groups',
            field=models.ManyToManyField(verbose_name='groups', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='authuser',
            name='last_login',
            field=models.DateTimeField(verbose_name='last login', null=True, blank=True),
        ),
    ]
