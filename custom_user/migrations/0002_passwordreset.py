# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('reset_key', models.CharField(max_length=50)),
                ('creation_time', models.DateTimeField(db_index=True, auto_now_add=True, db_column='creation_time')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
