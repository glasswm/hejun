# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='bbs_id',
            field=models.CharField(max_length=60, null=True),
            preserve_default=True,
        ),
    ]
