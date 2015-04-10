# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0010_argumentrating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='name',
            field=models.CharField(max_length=50, unique=True, db_index=True),
            preserve_default=True,
        ),
    ]
