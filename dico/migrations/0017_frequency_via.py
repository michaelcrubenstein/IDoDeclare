# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0016_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='Frequency',
            fields=[
                ('id', models.PositiveSmallIntegerField(default=0, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=25, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Via',
            fields=[
                ('id', models.PositiveSmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=25, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
