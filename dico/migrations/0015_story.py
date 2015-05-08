# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0014_auto_20150427_1254'),
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('description', models.TextField()),
                ('link', models.TextField()),
                ('creationTime', models.DateTimeField(db_index=True, db_column='creation_time', auto_now_add=True)),
                ('constituent', models.ForeignKey(db_column='constituent_id', to='dico.Constituent')),
                ('petition', models.ForeignKey(db_column='petition_id', to='dico.Petition')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
