# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0002_passwordreset'),
        ('dico', '0011_auto_20150410_2211'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMethod',
            fields=[
                ('user', models.ForeignKey(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('frequency', models.PositiveSmallIntegerField(default=0, db_index=True)),
                ('via', models.PositiveSmallIntegerField(null=True, db_index=True)),
                ('phonenumber', models.CharField(null=True, max_length=25)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
