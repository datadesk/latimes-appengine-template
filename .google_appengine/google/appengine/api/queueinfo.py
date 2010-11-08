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

"""QueueInfo tools.

A library for working with QueueInfo records, describing task queue entries
for an application. Supports loading the records from queue.yaml.

A queue has two required parameters and one optional one. The required
parameters are 'name' (must be unique for an appid) and 'rate' (the rate
at which jobs in the queue are run). There is an optional parameter
'bucket_size' that will allow tokens to be 'saved up' (for more on the
algorithm, see http://en.wikipedia.org/wiki/Token_Bucket). rate is expressed
as number/unit, with number being an int or a float, and unit being one of
's' (seconds), 'm' (minutes), 'h' (hours) or 'd' (days). bucket_size is
an integer.

An example of the use of bucket_size rate: the free email quota is 2000/d,
and the maximum you can send in a single minute is 11. So we can define a
queue for sending email like this:

queue:
- name: mail_queue
  rate: 2000/d
  bucket_size: 10

If this queue had been idle for a while before some jobs were submitted to it,
the first 10 jobs submitted would be run immediately, then subsequent ones
would be run once every 40s or so. The limit of 2000 per day would still apply.

An app's queues are also subject to storage quota limits for their stored tasks,
i.e. those tasks that have been added to queues but not yet executed. This quota
is part of their total storage quota (including datastore and blobstore quota).
We allow an app to override the default portion of this quota available for
taskqueue storage (100M) with a top level field "total_storage_quota".

taskqueue_storage_limit: 1.2G

If no suffix is specified, the number is interpreted as bytes. Supported
suffices are B (bytes), K (kilobytes), M (megabytes), G (gigabytes) and
T (terabytes). If taskqueue_storage_quota exceeds the total storage quota
available to an app, it is clamped.
"""



from google.appengine.api import validation
from google.appengine.api import yaml_builder
from google.appengine.api import yaml_listener
from google.appengine.api import yaml_object

_NAME_REGEX = r'^[A-Za-z0-9-]{0,499}$'
_RATE_REGEX = r'^(0|[0-9]+(\.[0-9]*)?/[smhd])'
_TOTAL_STORAGE_LIMIT_REGEX = r'^([0-9]+(\.[0-9]*)?[BKMGT]?)'

QUEUE = 'queue'

NAME = 'name'
RATE = 'rate'
BUCKET_SIZE = 'bucket_size'
TOTAL_STORAGE_LIMIT = 'total_storage_limit'

BYTE_SUFFIXES = 'BKMGT'


class MalformedQueueConfiguration(Exception):
  """Configuration file for Task Queue is malformed."""


class QueueEntry(validation.Validated):
  """A queue entry describes a single task queue."""
  ATTRIBUTES = {
      NAME: _NAME_REGEX,
      RATE: _RATE_REGEX,
      BUCKET_SIZE: validation.Optional(validation.TYPE_INT),
  }


class QueueInfoExternal(validation.Validated):
  """QueueInfoExternal describes all queue entries for an application."""
  ATTRIBUTES = {
      TOTAL_STORAGE_LIMIT: validation.Optional(_TOTAL_STORAGE_LIMIT_REGEX),
      QUEUE: validation.Optional(validation.Repeated(QueueEntry)),
  }


def LoadSingleQueue(queue_info):
  """Load a queue.yaml file or string and return a QueueInfoExternal object.

  Args:
    queue_info: the contents of a queue.yaml file, as a string.

  Returns:
    A QueueInfoExternal object.
  """
  builder = yaml_object.ObjectBuilder(QueueInfoExternal)
  handler = yaml_builder.BuilderHandler(builder)
  listener = yaml_listener.EventListener(handler)
  listener.Parse(queue_info)

  queue_info = handler.GetResults()
  if len(queue_info) < 1:
    raise MalformedQueueConfiguration('Empty queue configuration.')
  if len(queue_info) > 1:
    raise MalformedQueueConfiguration('Multiple queue: sections '
                                      'in configuration.')
  return queue_info[0]


def ParseRate(rate):
  """Parses a rate string in the form number/unit, or the literal 0.

  The unit is one of s (seconds), m (minutes), h (hours) or d (days).

  Args:
    rate: the rate string.

  Returns:
    a floating point number representing the rate/second.

  Raises:
    MalformedQueueConfiguration: if the rate is invalid
  """
  if rate == "0":
    return 0.0
  elements = rate.split('/')
  if len(elements) != 2:
    raise MalformedQueueConfiguration('Rate "%s" is invalid.' % rate)
  number, unit = elements
  try:
    number = float(number)
  except ValueError:
    raise MalformedQueueConfiguration('Rate "%s" is invalid:'
                                          ' "%s" is not a number.' %
                                          (rate, number))
  if unit not in 'smhd':
    raise MalformedQueueConfiguration('Rate "%s" is invalid:'
                                          ' "%s" is not one of s, m, h, d.' %
                                          (rate, unit))
  if unit == 's':
    return number
  if unit == 'm':
    return number/60
  if unit == 'h':
    return number/(60 * 60)
  if unit == 'd':
    return number/(24 * 60 * 60)

def ParseTotalStorageLimit(limit):
  """Parses a string representing the storage bytes limit.

  Optional limit suffixes are:
      B (bytes), K (kilobytes), M (megabytes), G (gigabytes), T (terabytes)

  Args:
    limit: The storage bytes limit string.

  Returns:
    An int representing the storage limit in bytes.

  Raises:
    MalformedQueueConfiguration: if the limit argument isn't a valid python
    double followed by an optional suffix.
  """
  try:
    if limit[-1] in BYTE_SUFFIXES:
      number = float(limit[0:-1])
      for c in BYTE_SUFFIXES:
        if limit[-1] != c:
          number = number * 1024
        else:
          return int(number)
    else:
      return int(limit)
  except ValueError:
    raise MalformedQueueConfiguration('Total Storage Limit "%s" is invalid.' %
                                      limit)

