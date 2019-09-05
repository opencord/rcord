# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-09-05 16:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcord', '0012_bandwidth_profile_values'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rcordservice_decl',
            options={'verbose_name': 'Subscriber Service'},
        ),
        migrations.AlterModelOptions(
            name='rcordsubscriber_decl',
            options={'verbose_name': 'Subscriber'},
        ),
        migrations.AlterField(
            model_name='bandwidthprofile_decl',
            name='air',
            field=models.IntegerField(help_text=b'Access Information Rate'),
        ),
        migrations.AlterField(
            model_name='bandwidthprofile_decl',
            name='cbs',
            field=models.IntegerField(help_text=b'Committed Burst Rate'),
        ),
        migrations.AlterField(
            model_name='bandwidthprofile_decl',
            name='cir',
            field=models.IntegerField(help_text=b'Committed Information Rate'),
        ),
        migrations.AlterField(
            model_name='bandwidthprofile_decl',
            name='ebs',
            field=models.IntegerField(help_text=b'Excess Burst Rate'),
        ),
        migrations.AlterField(
            model_name='bandwidthprofile_decl',
            name='eir',
            field=models.IntegerField(help_text=b'Excess Information Rate'),
        ),
    ]
