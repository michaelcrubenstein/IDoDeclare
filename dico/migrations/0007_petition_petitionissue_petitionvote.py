# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dico', '0006_auto_20150304_0007'),
    ]

    operations = [
        migrations.CreateModel(
            name='Petition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('description', models.TextField()),
                ('constituent', models.ForeignKey(db_column='constituent_id', to='dico.Constituent')),
                ('creationTime', models.DateTimeField(db_index=True, auto_now_add=True, db_column='creation_time')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PetitionIssue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('issue', models.ForeignKey(db_column='issue_id', to='dico.Issue')),
                ('petition', models.ForeignKey(db_column='petition_id', to='dico.Petition')),
                ('constituent', models.ForeignKey(db_column='constituent_id', to='dico.Constituent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PetitionVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('vote', models.IntegerField(db_index=True)),
                ('petition', models.ForeignKey(db_column='petition_id', to='dico.Petition')),
                ('constituent', models.ForeignKey(db_column='constituent_id', to='dico.Constituent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='mc',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, primary_key=True, db_column='user_id', serialize=False),
            preserve_default=True,
        ),
    ]
