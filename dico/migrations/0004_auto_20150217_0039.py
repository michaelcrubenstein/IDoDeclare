# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0003_auto_20150207_0012'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='constituent',
            name='id',
        ),
        migrations.AlterField(
            model_name='constituent',
            name='user',
            field=models.ForeignKey(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
