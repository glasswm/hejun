# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0004_auto_20150730_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reply',
            name='reply_id',
            field=models.CharField(unique=True, max_length=60),
            preserve_default=True,
        ),
    ]
