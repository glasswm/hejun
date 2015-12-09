# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0005_auto_20150730_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='last_update_page',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='thread',
            name='last_update_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 1, 0, 0)),
            preserve_default=True,
        ),
    ]
