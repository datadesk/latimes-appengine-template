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








"""
Generic exceptions.
"""

class TimeoutException(Exception):
  def __init__(self, msg=""):
    Exception.__init__(self, msg)


class NestedException(Exception):
  def __init__(self, exc_info):
    Exception.__init__(self, exc_info[1])
    self.exc_info_ = exc_info

  def exc_info(self):
    return self.exc_info_

class AbstractMethod(Exception):
  """Raise this exception to indicate that a method is abstract.  Example:
        class Foo:
          def Bar(self):
            raise gexcept.AbstractMethod"""
  def __init__(self):
    Exception.__init__(self)

