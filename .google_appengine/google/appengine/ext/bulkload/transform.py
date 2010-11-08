#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Bulkloader Transform Helper functions.

A collection of helper functions for bulkloading data, typically referenced
from a bulkloader.yaml file.
"""




import base64

import datetime
import os
import re
import tempfile

from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.ext.bulkload import bulkloader_errors


CURRENT_PROPERTY = None


def none_if_empty(fn):
  """A wrapper for a value to return None if it's empty. Useful on import.

  Can be used in config files (e.g. "transform.none_if_empty(int)" or
  as a decorator.

  Args:
    fn: Single argument transform function.

  Returns:
    Wrapped function.
  """

  def wrapper(value):
    if value == '' or value is None:
      return None
    return fn(value)

  return wrapper


def empty_if_none(fn):
  """A wrapper for a value to return '' if it's None. Useful on export.

  Can be used in config files (e.g. "transform.empty_if_none(unicode)" or
  as a decorator.

  Args:
    fn: Single argument transform function.

  Returns:
    Wrapped function.
  """

  def wrapper(value):
    if value is None:
      return ''
    return fn(value)

  return wrapper


def import_date_time(format, _strptime=None):
  """A wrapper around strptime. Also returns None if the input is empty.

  Args:
    format: Format string for strptime.

  Returns:
    Single argument method which parses a string into a datetime using format.
  """
  if not _strptime:
    _strptime = datetime.datetime.strptime

  def import_date_time_lambda(value):
    if not value:
      return None
    return _strptime(value, format)

  return import_date_time_lambda


def export_date_time(format):
  """A wrapper around strftime. Also returns '' if the input is None.

  Args:
    format: Format string for strftime.

  Returns:
    Single argument method which convers a datetime into a string using format.
  """

  def export_date_time_lambda(value):
    if not value:
      return ''
    return datetime.datetime.strftime(value, format)

  return export_date_time_lambda


def create_foreign_key(kind, key_is_id=False):
  """A method to make one-level Key objects.

  These are typically used in ReferenceProperty in Python, where the reference
  value is a key with kind (or model) name name.

  This helper method does not support keys with parents. Use create_deep_key
  instead to create keys with parents.

  Args:
    kind: The kind name of the reference as a string.
    key_is_id: If true, convert the key into an integer to be used as an id.
      If false, leave the key in the input format (typically a string).

  Returns:
    Single argument method which parses a value into a Key of kind entity_kind.
  """

  def generate_foreign_key_lambda(value):
    if key_is_id:
      value = int(value)
    return datastore.Key.from_path(kind, value)

  return generate_foreign_key_lambda


def create_deep_key(*path_info):
  """A method to make multi-level Key objects.

  Generates multi-level key from multiple fields in the input dictionary.

  This is typically used for Keys for entities which have variable parent keys,
  e.g. ones with owned relationships. It can used for both __key__ and
  references.

  Use create_foreign_key as a simpler way to create single level keys.

  Args:
    path_info: List of tuples, describing (kind, property, is_id=False).
      kind: The kind name.
      property: The external property in the current import dictionary, or
        transform.CURRENT_PROPERTY for the value passed to the transform.
      is_id: Converts value to int and treats as numeric ID if True, otherwise
        the value is a string name. Default is False.
      Example:
        create_deep_key(('rootkind', 'rootcolumn'),
                        ('childkind', 'childcolumn', True),
                        ('leafkind', transform.CURRENT_PROPERTY))

  Returns:
    Transform method which parses the info from the current neutral dictionary
    into a Key with parents as described by path_info.
  """
  validated_path_info = []
  for level_info in path_info:
    if len(level_info) == 3:
      key_is_id = level_info[2]
    elif len(level_info) == 2:
      key_is_id = False
    else:
      raise bulkloader_errors.InvalidConfiguration(
          'Each list in create_deep_key must specify exactly 2 or 3 '
          'parameters, (kind, property, is_id=False). You specified: %s' %
          repr(path_info))
    kind_name = level_info[0]
    property_name = level_info[1]
    validated_path_info.append((kind_name, property_name, key_is_id))


  def create_deep_key_lambda(value, bulkload_state):
    path = []
    for kind_name, property_name, key_is_id in validated_path_info:
      if property_name is CURRENT_PROPERTY:
        name_or_id = value
      else:
        name_or_id = bulkload_state.current_dictionary[property_name]

      if key_is_id:
        name_or_id = int(name_or_id)

      path += [kind_name, name_or_id]

    return datastore.Key.from_path(*path)

  return create_deep_key_lambda


@empty_if_none
def key_id_or_name_as_string(key):
  """If a key is present, return its id or name as a string.

  Note that this loses the distinction between integer IDs and strings
  which happen to look like integers. Use key_type to distinguish them.

  It also only prints the leaf of the key, i.e. if the key has a parent
  it is not printed.

  Args:
    key: A google.appengine.datastore Key, or None.

  Returns:
    String representation of the leaf id or name of the key.
  """
  return unicode(key.id_or_name())


@empty_if_none
def key_type(key):
  """String identifying if the key is a 'name' or an 'ID', or '' for None.

  This is most useful when paired with key_id_or_name_as_string.

  Args:
    key: A datastore Key

  Returns:
    The type of the leaf identifier of the Key, 'ID', 'name', or ''.
  """
  if key.id():
    return 'ID'
  elif key.name():
    return 'name'
  else:
    return ''


def regexp_extract(pattern):
  """Return first group in the value matching the pattern.

  Args:
    pattern: A regular expression to match on with at least one group.

  Returns:
    A single argument method which returns the first group matched,
    or None if no match or no group was found.
  """

  def regexp_extract_lambda(value):
    if not value:
      return None
    matches = re.match(pattern, value)
    if not matches:
      return None
    return matches.group(1)

  return regexp_extract_lambda


@none_if_empty
def blobproperty_from_base64(value):
  """Return a datastore blob property containing the base64 decoded value."""
  decoded_value = base64.b64decode(value)
  return datastore_types.Blob(decoded_value)


@none_if_empty
def bytestring_from_base64(value):
  """Return a datastore bytestring property from a base64 encoded value."""
  decoded_value = base64.b64decode(value)
  return datastore_types.ByteString(decoded_value)


def blob_to_file(filename_hint_propertyname=None,
                 directory_hint=''):
  """Write the blob contents to a file, and replace them with the filename."""
  directory = []

  def transform_function(value, bulkload_state):
    if not directory:
      parent_dir = os.path.dirname(bulkload_state.filename)
      directory.append(os.path.join(parent_dir, directory_hint))
      if directory[0] and not os.path.exists(directory[0]):
        os.makedirs(directory[0])

    filename_hint = 'blob_'
    suffix = ''
    filename = ''
    if filename_hint_propertyname:
      filename_hint = bulkload_state.current_entity[filename_hint_propertyname]
      filename = os.path.join(directory[0], filename_hint)
      if os.path.exists(filename):
        filename = ''
        (filename_hint, suffix) = os.path.splitext(filename_hint)
    if not filename:
      filename = tempfile.mktemp(suffix, filename_hint, directory[0])
    f = open(filename, 'wb')
    f.write(value)
    f.close()
    return filename

  return transform_function


def regexp_bool(regexp, flags=0):
  """Return a boolean if the expression matches with re.match.

  Note that re.match anchors at the start but not end of the string.

  Args:
    regexp: String, regular expression.
    flags: Optional flags to pass to re.match.

  Returns:
    Boolean, if the expression matches.
  """

  def transform_function(value):
    return bool(re.match(regexp, value, flags))

  return transform_function
