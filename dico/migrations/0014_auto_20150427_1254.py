# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0013_auto_20150418_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='petition',
            name='issues',
            field=models.ManyToManyField(to='dico.Issue', db_index=True, through='dico.PetitionIssue'),
            preserve_default=True,
        ),
    ]
