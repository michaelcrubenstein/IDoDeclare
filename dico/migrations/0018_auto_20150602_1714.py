# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0017_frequency_via'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactmethod',
            name='frequency',
            field=models.ForeignKey(to='dico.Frequency', default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contactmethod',
            name='via',
            field=models.ForeignKey(to='dico.Via', null=True),
            preserve_default=True,
        ),
    ]
