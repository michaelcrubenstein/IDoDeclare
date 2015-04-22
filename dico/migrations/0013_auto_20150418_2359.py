# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0012_contactmethod'),
    ]

    operations = [
        migrations.AddField(
            model_name='petitionvote',
            name='creationTime',
            field=models.DateTimeField(db_index=True, db_column='creation_time', default=datetime.datetime(2015, 4, 18, 23, 59, 21, 761315, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='petitionvote',
            name='lastModifiedTime',
            field=models.DateTimeField(db_index=True, db_column='last_modified_time', default=datetime.datetime(2015, 4, 18, 23, 59, 31, 481250, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
