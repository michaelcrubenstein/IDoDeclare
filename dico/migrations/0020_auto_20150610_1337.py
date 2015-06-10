# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0019_message_messagetouch'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='petition',
            field=models.ForeignKey(null=True, to='dico.Petition', db_column='petition_id'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='messagetouch',
            name='executionTime',
            field=models.DateTimeField(db_index=True, null=True),
            preserve_default=True,
        ),
    ]
