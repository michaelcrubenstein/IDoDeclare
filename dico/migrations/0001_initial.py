# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Constituent',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('email', models.EmailField(max_length=254, db_index=True, unique=True)),
                ('firstName', models.CharField(max_length=50, db_column='first_name')),
                ('lastName', models.CharField(max_length=50, db_column='last_name')),
                ('streetAddress', models.CharField(max_length=100, db_column='street_address')),
                ('zipCode', models.IntegerField(db_column='zip_code')),
                ('district', models.IntegerField(db_index=True)),
                ('state', models.CharField(max_length=2, db_index=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConstituentInterest',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('constituent', models.ForeignKey(to='dico.Constituent', db_column='constituent_id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('description', models.TextField()),
                ('link', models.URLField()),
                ('eventTime', models.DateTimeField(db_index=True, db_column='event_time')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventIssue',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('event', models.ForeignKey(to='dico.Event', db_column='event_id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=30, db_index=True, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MC',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('email', models.EmailField(max_length=254, db_index=True, unique=True)),
                ('firstName', models.CharField(max_length=50, db_column='first_name')),
                ('lastName', models.CharField(max_length=50, db_column='last_name')),
                ('district', models.IntegerField(db_index=True, null=True)),
                ('state', models.CharField(max_length=2, db_index=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MCInterest',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('entryTime', models.DateTimeField(db_index=True, db_column='entry_time')),
                ('issue', models.ForeignKey(to='dico.Issue', db_column='issue_id')),
                ('mc', models.ForeignKey(to='dico.MC', db_column='mc_id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='eventissue',
            name='issue',
            field=models.ForeignKey(to='dico.Issue', db_column='issue_id'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='mc',
            field=models.ForeignKey(to='dico.MC', db_column='mc_id'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='constituentinterest',
            name='issue',
            field=models.ForeignKey(to='dico.Issue', db_column='issue_id'),
            preserve_default=True,
        ),
    ]
