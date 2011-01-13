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

"""A simple wrapper for Django templates.

The main purpose of this module is to hide all of the package import pain
you normally have to go through to get Django to work. We expose the Django
Template and Context classes from this module, handling the import nonsense
on behalf of clients.

Typical usage:

   from google.appengine.ext.webapp import template
   print template.render('templates/index.html', {'foo': 'bar'})

Django uses a global setting for the directory in which it looks for templates.
This is not natural in the context of the webapp module, so our load method
takes in a complete template path, and we set these settings on the fly
automatically.  Because we have to set and use a global setting on every
method call, this module is not thread safe, though that is not an issue
for applications.

Django template documentation is available at:
http://www.djangoproject.com/documentation/templates/
"""





import md5
import os

from google.appengine.api import lib_config
from google.appengine.ext import webapp


def _django_setup():
  """Imports and configures Django.

  This can be overridden by defining a function named
  webapp_django_setup() in the app's appengine_config.py file (see
  lib_config docs).  Such a function should import and configure
  Django.

  You can also just configure the Django version to be used by setting
  webapp_django_version in that file.

  Finally, calling use_library('django', <version>) in that file
  should also work, followed by code to configure Django settings:

    # The first two sections of this example are taken from
    # http://code.google.com/appengine/docs/python/tools/libraries.html#Django

    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    from google.appengine.dist import use_library
    use_library('django', '1.1')

    # This last section is necessary to be able to switch between
    # Django and webapp.template freely, regardless of which was
    # imported first.

    from django.conf import settings
    settings._target = None

  If your application also imports Django directly it should ensure
  that the same code is executed before your app imports Django
  (directly or indirectly).  Perhaps the simplest way to ensure that
  is to include the following in your main.py (and in each alternate
  main script):

    from google.appengine.ext.webapp import template
    import django

  This will ensure that whatever Django setup code you have included
  in appengine_config.py is executed, as a side effect of importing
  the webapp.template module.
  """
  django_version = _config_handle.django_version

  if django_version is not None:
    from google.appengine.dist import use_library
    use_library('django', str(django_version))
  else:
    try:
      from django import v0_96
    except ImportError:
      pass

  import django

  import django.conf
  try:
    django.conf.settings.configure(
      DEBUG=False,
      TEMPLATE_DEBUG=False,
      TEMPLATE_LOADERS=(
        'django.template.loaders.filesystem.load_template_source',
      ),
    )
  except (EnvironmentError, RuntimeError):
    pass

_config_handle = lib_config.register(
    'webapp',
    {'django_setup': _django_setup,
     'django_version': None,
     })

_config_handle.django_setup()


import django.template
import django.template.loader

def render(template_path, template_dict, debug=False):
  """Renders the template at the given path with the given dict of values.

  Example usage:
    render("templates/index.html", {"name": "Bret", "values": [1, 2, 3]})

  Args:
    template_path: path to a Django template
    template_dict: dictionary of values to apply to the template
  """
  t = load(template_path, debug)
  return t.render(Context(template_dict))


template_cache = {}
def load(path, debug=False):
  """Loads the Django template from the given path.

  It is better to use this function than to construct a Template using the
  class below because Django requires you to load the template with a method
  if you want imports and extends to work in the template.
  """
  abspath = os.path.abspath(path)

  if not debug:
    template = template_cache.get(abspath, None)
  else:
    template = None

  if not template:
    directory, file_name = os.path.split(abspath)
    new_settings = {
        'TEMPLATE_DIRS': (directory,),
        'TEMPLATE_DEBUG': debug,
        'DEBUG': debug,
        }
    old_settings = _swap_settings(new_settings)
    try:
      template = django.template.loader.get_template(file_name)
    finally:
      _swap_settings(old_settings)

    if not debug:
      template_cache[abspath] = template

    def wrap_render(context, orig_render=template.render):
      URLNode = django.template.defaulttags.URLNode
      save_urlnode_render = URLNode.render
      old_settings = _swap_settings(new_settings)
      try:
        URLNode.render = _urlnode_render_replacement
        return orig_render(context)
      finally:
        _swap_settings(old_settings)
        URLNode.render = save_urlnode_render

    template.render = wrap_render

  return template


def _swap_settings(new):
  """Swap in selected Django settings, returning old settings.

  Example:
    save = _swap_settings({'X': 1, 'Y': 2})
    try:
      ...new settings for X and Y are in effect here...
    finally:
      _swap_settings(save)

  Args:
    new: A dict containing settings to change; the keys should
      be setting names and the values settings values.

  Returns:
    Another dict structured the same was as the argument containing
    the original settings.  Original settings that were not set at all
    are returned as None, and will be restored as None by the
    'finally' clause in the example above.  This shouldn't matter; we
    can't delete settings that are given as None, since None is also a
    legitimate value for some settings.  Creating a separate flag value
    for 'unset' settings seems overkill as there is no known use case.
  """
  settings = django.conf.settings
  old = {}
  for key, value in new.iteritems():
    old[key] = getattr(settings, key, None)
    setattr(settings, key, value)
  return old


def create_template_register():
  """Used to extend the Django template library with custom filters and tags.

  To extend the template library with a custom filter module, create a Python
  module, and create a module-level variable named "register", and register
  all custom filters to it as described at
  http://www.djangoproject.com/documentation/templates_python/
    #extending-the-template-system:

    templatefilters.py
    ==================
    register = webapp.template.create_template_register()

    def cut(value, arg):
      return value.replace(arg, '')
    register.filter(cut)

  Then, register the custom template module with the register_template_library
  function below in your application module:

    myapp.py
    ========
    webapp.template.register_template_library('templatefilters')
  """
  return django.template.Library()


def register_template_library(package_name):
  """Registers a template extension module to make it usable in templates.

  See the documentation for create_template_register for more information."""
  if not django.template.libraries.get(package_name, None):
    django.template.add_to_builtins(package_name)


Template = django.template.Template
Context = django.template.Context


def _urlnode_render_replacement(self, context):
  """Replacement for django's {% url %} block.

  This version uses WSGIApplication's url mapping to create urls.

  Examples:

  <a href="{% url MyPageHandler "overview" %}">
  {% url MyPageHandler implicit_args=False %}
  {% url MyPageHandler "calendar" %}
  {% url MyPageHandler "jsmith","calendar" %}
  """
  args = [arg.resolve(context) for arg in self.args]
  try:
    app = webapp.WSGIApplication.active_instance
    handler = app.get_registered_handler_by_name(self.view_name)
    return handler.get_url(implicit_args=True, *args)
  except webapp.NoUrlFoundError:
    return ''
