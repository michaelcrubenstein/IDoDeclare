# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0018_auto_20150602_1714'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('subject', models.CharField(db_index=True, max_length=200)),
                ('body', models.TextField()),
                ('creationTime', models.DateTimeField(db_index=True, db_column='creation_time', auto_now_add=True)),
                ('constituent', models.ForeignKey(db_column='constituent_id', to='dico.Constituent')),
                ('via', models.ForeignKey(null=True, to='dico.Via')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageTouch',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('creationTime', models.DateTimeField(db_index=True, db_column='creation_time', auto_now_add=True)),
                ('executionTime', models.DateTimeField(db_index=True)),
                ('address', models.CharField(max_length=100)),
                ('constituent', models.ForeignKey(db_column='constituent_id', to='dico.Constituent')),
                ('message', models.ForeignKey(db_column='message_id', to='dico.Message')),
                ('via', models.ForeignKey(null=True, to='dico.Via')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
