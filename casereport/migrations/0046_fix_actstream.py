# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2018-01-10 19:58
from __future__ import unicode_literals

from django.db import migrations
from django.db.utils import ProgrammingError
from jsonfield_compat.fields import JSONField

# if you run into actstream creating migrations over and over
# it is related to this casereport/migrations/0045_action_data_nullable.py
# the 0001 migration called the action migration Action
# but 0002 and forward called it 'action' to remove it.
# putting the column back awakend this bug.   it looks like django 1.10
# solves this.

class ExternalAppAddField(migrations.AddField):
    """ Wraps all calls that reference the app_label with the label
    of the external app.
    """
    def __init__(self, model_name, name, field, preserve_default=True,
                 app_label="actstream"):
        super(ExternalAppAddField, self).__init__(model_name, name, field,
                                                    preserve_default)
        self._app_label = app_label

    def state_forwards(self, app_label, state):
        return super(ExternalAppAddField, self).state_forwards(
            self._app_label, state)

    def database_backwards(self, app_label, schema_editor,
                           from_state, to_state):
        return super(ExternalAppAddField, self).database_backwards(
            self._app_label,
            schema_editor,
            from_state,
            to_state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        try:
            return super(ExternalAppAddField, self).database_forwards(
                self._app_label,
                schema_editor,
                from_state,
                to_state)
        except ProgrammingError as fixed:
            """
            django.db.utils.ProgrammingError: column "data" of relation "actstream_action" already exists
            """
            print("Looks like the actstream.Action model has been fixed.")

    def references_field(self, model_name, name, app_label=None):
        return super(ExternalAppAddField, self).references_field(
            model_name,
            name,
            app_label=self._app_label)


class Migration(migrations.Migration):

    dependencies = [
        ('casereport', '0045_auto_20171218_2000'),
    ]

    operations = [
        ExternalAppAddField(
            model_name='action',
            name='data',
            field=JSONField(default=False, editable=False, null=True),
            #preserve_default=True,
            app_label="actstream",
        ),
    ]
