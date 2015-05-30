# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0015_story'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('description', models.TextField()),
                ('link', models.TextField()),
                ('creationTime', models.DateTimeField(auto_now_add=True, db_column='creation_time', db_index=True)),
                ('constituent', models.ForeignKey(to='dico.Constituent', db_column='constituent_id')),
                ('petition', models.ForeignKey(to='dico.Petition', db_column='petition_id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
