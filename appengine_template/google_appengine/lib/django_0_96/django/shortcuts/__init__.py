# This module collects helper functions and classes that "span" multiple levels
# of MVC. In other words, these functions/classes introduce controlled coupling
# for convenience's sake.

from django.template import loader
from django.http import HttpResponse, Http404
from django.db.models.manager import Manager

def render_to_response(*args, **kwargs):
    return HttpResponse(loader.render_to_string(*args, **kwargs))
load_and_render = render_to_response # For backwards compatibility.

def get_object_or_404(klass, *args, **kwargs):
    if isinstance(klass, Manager):
        manager = klass
        klass = manager.model
    else:
        manager = klass._default_manager
    try:
        return manager.get(*args, **kwargs)
    except klass.DoesNotExist:
        raise Http404('No %s matches the given query.' % klass._meta.object_name)

def get_list_or_404(klass, *args, **kwargs):
    if isinstance(klass, Manager):
        manager = klass
    else:
        manager = klass._default_manager
    obj_list = list(manager.filter(*args, **kwargs))
    if not obj_list:
        raise Http404('No %s matches the given query.' % manager.model._meta.object_name)
    return obj_list
