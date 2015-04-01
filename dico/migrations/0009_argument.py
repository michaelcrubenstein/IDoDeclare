# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0008_petition_issues'),
    ]

    operations = [
        migrations.CreateModel(
            name='Argument',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('vote', models.IntegerField(db_index=True)),
                ('creationTime', models.DateTimeField(auto_now_add=True, db_index=True, db_column='creation_time')),
                ('constituent', models.ForeignKey(to='dico.Constituent', db_column='constituent_id')),
                ('petition', models.ForeignKey(to='dico.Petition', db_column='petition_id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
