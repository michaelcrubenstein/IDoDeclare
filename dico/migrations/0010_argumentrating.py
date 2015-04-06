# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0009_argument'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArgumentRating',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('vote', models.IntegerField(db_index=True)),
                ('creationTime', models.DateTimeField(db_index=True, auto_now_add=True, db_column='creation_time')),
                ('lastModifiedTime', models.DateTimeField(auto_now=True, db_index=True, db_column='last_modified_time')),
                ('argument', models.ForeignKey(to='dico.Argument', db_column='argument_id')),
                ('constituent', models.ForeignKey(to='dico.Constituent', db_column='constituent_id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
