# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('username', models.CharField(validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', message='Only alphanumeric characters are allowed.')], max_length=20)),
                ('email', models.EmailField(unique=True, verbose_name='email address', max_length=255)),
                ('first_name', models.CharField(blank=True, null=True, max_length=30)),
                ('last_name', models.CharField(blank=True, null=True, max_length=50)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('profile_image', models.ImageField(upload_to='uploads', default='/static/images/defaultuserimage.png')),
                ('user_bio', models.CharField(blank=True, max_length=600)),
                ('groups', models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups', related_name='user_set', blank=True, to='auth.Group', related_query_name='user')),
                ('user_permissions', models.ManyToManyField(help_text='Specific permissions for this user.', verbose_name='user permissions', related_name='user_set', blank=True, to='auth.Permission', related_query_name='user')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
