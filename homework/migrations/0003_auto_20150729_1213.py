# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0002_student_bbs_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='bbs_id',
            field=models.CharField(max_length=60),
            preserve_default=True,
        ),
    ]
