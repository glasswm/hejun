# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0003_auto_20150729_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='reply_id',
            field=models.CharField(max_length=60, unique=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='bbs_id',
            field=models.CharField(unique=True, max_length=60),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='wihchclass',
            field=models.ForeignKey(related_name='student', to='homework.Class', null=True),
            preserve_default=True,
        ),
    ]
