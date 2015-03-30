# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dico', '0007_petition_petitionissue_petitionvote'),
    ]

    operations = [
        migrations.AddField(
            model_name='petition',
            name='issues',
            field=models.ManyToManyField(through='dico.PetitionIssue', to='dico.Issue'),
            preserve_default=True,
        ),
    ]
