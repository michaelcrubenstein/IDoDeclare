# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0020_auto_20150610_1337'),
    ]

    operations = [
        migrations.CreateModel(
            name='Envelope',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('creationTime', models.DateTimeField(db_column='creation_time', db_index=True, auto_now_add=True)),
                ('executionTime', models.DateTimeField(db_index=True, null=True)),
                ('address', models.CharField(max_length=100)),
                ('constituent', models.ForeignKey(db_column='constituent_id', to='dico.Constituent')),
                ('message', models.ForeignKey(db_column='message_id', to='dico.Message')),
                ('via', models.ForeignKey(null=True, to='dico.Via')),
            ],
        ),
        migrations.RemoveField(
            model_name='messagetouch',
            name='constituent',
        ),
        migrations.RemoveField(
            model_name='messagetouch',
            name='message',
        ),
        migrations.RemoveField(
            model_name='messagetouch',
            name='via',
        ),
        migrations.DeleteModel(
            name='MessageTouch',
        ),
    ]
