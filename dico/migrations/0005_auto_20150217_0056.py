# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0004_auto_20150217_0039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mc',
            name='id',
        ),
        migrations.AlterField(
            model_name='mc',
            name='user',
            field=models.ForeignKey(serialize=False, primary_key=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
