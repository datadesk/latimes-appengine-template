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




"""The Python datastore API used by app developers.

Defines Entity, Query, and Iterator classes, as well as methods for all of the
datastore's calls. Also defines conversions between the Python classes and
their PB counterparts.

The datastore errors are defined in the datastore_errors module. That module is
only required to avoid circular imports. datastore imports datastore_types,
which needs BadValueError, so it can't be defined in datastore.
"""
















import heapq
import itertools
import logging
import os
import re
import sys
import threading
import traceback
from xml.sax import saxutils

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import capabilities
from google.appengine.api import datastore_errors
from google.appengine.api import datastore_types
from google.appengine.datastore import datastore_pb
from google.appengine.datastore import datastore_query
from google.appengine.datastore import datastore_rpc
from google.appengine.datastore import entity_pb


MAX_ALLOWABLE_QUERIES = 30


MAXIMUM_RESULTS = 1000





DEFAULT_TRANSACTION_RETRIES = 3


READ_CAPABILITY = capabilities.CapabilitySet('datastore_v3')
WRITE_CAPABILITY = capabilities.CapabilitySet(
    'datastore_v3',
    capabilities=['write'])







_MAX_INDEXED_PROPERTIES = 5000


_MAX_ID_BATCH_SIZE = datastore_rpc._MAX_ID_BATCH_SIZE

Key = datastore_types.Key
typename = datastore_types.typename


_ALLOWED_API_KWARGS = frozenset(['rpc', 'config'])


STRONG_CONSISTENCY = datastore_rpc.Configuration.STRONG_CONSISTENCY
EVENTUAL_CONSISTENCY = datastore_rpc.Configuration.EVENTUAL_CONSISTENCY



_MAX_INT_32 = 2**31-1


def NormalizeAndTypeCheck(arg, types):
  """Normalizes and type checks the given argument.

  Args:
    arg: an instance or iterable of the given type(s)
    types: allowed type or tuple of types

  Returns:
    A (list, bool) tuple. The list is a normalized, shallow copy of the
    argument. The boolean is True if the argument was a sequence, False
    if it was a single object.

  Raises:
    AssertionError: types includes list or tuple.
    BadArgumentError: arg is not an instance or sequence of one of the given
    types.
  """
  if not isinstance(types, (list, tuple)):
    types = (types,)

  assert list not in types and tuple not in types

  if isinstance(arg, types):

    return [arg], False
  else:


    if isinstance(arg, basestring):
      raise datastore_errors.BadArgumentError(
          'Expected an instance or iterable of %s; received %s (a %s).' %
          (types, arg, typename(arg)))

    try:

      arg_list = list(arg)
    except TypeError:

      raise datastore_errors.BadArgumentError(
          'Expected an instance or iterable of %s; received %s (a %s).' %
          (types, arg, typename(arg)))


    for val in arg_list:
      if not isinstance(val, types):
        raise datastore_errors.BadArgumentError(
            'Expected one of %s; received %s (a %s).' %
            (types, val, typename(val)))

    return arg_list, True


def NormalizeAndTypeCheckKeys(keys):
  """Normalizes and type checks that the given argument is a valid key or keys.

  A wrapper around NormalizeAndTypeCheck() that accepts strings, Keys, and
  Entities, and normalizes to Keys.

  Args:
    keys: a Key or sequence of Keys

  Returns:
    A (list of Keys, bool) tuple. See NormalizeAndTypeCheck.

  Raises:
    BadArgumentError: arg is not an instance or sequence of one of the given
    types.
  """
  keys, multiple = NormalizeAndTypeCheck(keys, (basestring, Entity, Key))

  keys = [_GetCompleteKeyOrError(key) for key in keys]

  return (keys, multiple)


def _GetConfigFromKwargs(kwargs):
  """Get a Configuration object from the keyword arguments.

  This is purely an internal helper for the various public APIs below
  such as Get().

  Args:
    kwargs: A dict containing the keyword arguments passed to a public API.

  Returns:
    A UserRPC instance, or a Configuration instance, or None.

  Raises:
    TypeError if unexpected keyword arguments are present.
  """
  if not kwargs:
    return None
  args_diff = set(kwargs) - _ALLOWED_API_KWARGS
  if args_diff:
    raise datastore_errors.BadArgumentError(
      'Unexpected keyword arguments: %s' % ', '.join(args_diff))
  rpc = kwargs.get('rpc')
  config = kwargs.get('config')
  if rpc is not None:
    if config is not None:
      raise datastore_errors.BadArgumentError(
        'Expected rpc= or config= argument but not both')

    if isinstance(rpc, (apiproxy_stub_map.UserRPC,
                        datastore_rpc.Configuration)):
      return rpc
    raise datastore_errors.BadArgumentError(
      'rpc= argument should be None or a UserRPC instance')
  if config is not None:
    if not isinstance(config, (datastore_rpc.Configuration,
                               apiproxy_stub_map.UserRPC)):
      raise datastore_errors.BadArgumentError(
      'config= argument should be None or a Configuration instance')
  return config


class DatastoreAdapter(datastore_rpc.AbstractAdapter):
  """Adapter between datatypes defined here (Entity etc.) and protobufs.

  See the base class in datastore_rpc.py for more docs.
  """

  def key_to_pb(self, key):
    return key._Key__reference

  def pb_to_key(self, pb):
    return Key._FromPb(pb)

  def entity_to_pb(self, entity):
    return entity._ToPb()

  def pb_to_entity(self, pb):
    return Entity._FromPb(pb)


_adapter = DatastoreAdapter()
_thread_local = threading.local()


_ENV_KEY = '__DATASTORE_CONNECTION_INITIALIZED__'


def _GetConnection():
  """Retrieve a datastore connection local to the thread."""










  connection = None
  if os.getenv(_ENV_KEY):
    try:
      connection = _thread_local.connection
    except AttributeError:
      pass
  if connection is None:
    connection = datastore_rpc.Connection(adapter=_adapter)
    _SetConnection(connection)
  return connection


def _SetConnection(connection):
  """Sets the datastore connection local to the thread."""
  _thread_local.connection = connection

  os.environ[_ENV_KEY] = '1'





def _MakeSyncCall(service, call, request, response, config=None):
  """The APIProxy entry point for a synchronous API call.

  Args:
    service: For backwards compatibility, must be 'datastore_v3'.
    call: String representing which function to call.
    request: Protocol buffer for the request.
    response: Protocol buffer for the response.
    config: Optional Configuration to use for this request.

  Returns:
    Response protocol buffer. Caller should always use returned value
    which may or may not be same as passed in 'response'.

  Raises:
    apiproxy_errors.Error or a subclass.
  """
  conn = _GetConnection()
  if isinstance(request, datastore_pb.Query):
    conn._set_request_read_policy(request, config)
    conn._set_request_transaction(request)
  rpc = conn.make_rpc_call(config, call, request, response)
  conn.check_rpc_success(rpc)
  return response


def CreateRPC(service='datastore_v3',
              deadline=None, callback=None, read_policy=None):
  """Create an rpc for use in configuring datastore calls.

  NOTE: This functions exists for backwards compatibility.  Please use
  CreateConfig() instead.  NOTE: the latter uses 'on_completion',
  which is a function taking an argument, wherease CreateRPC uses
  'callback' which is a function without arguments.

  Args:
    service: Optional string; for backwards compatibility, must be
      'datastore_v3'.
    deadline: Optional int or float, deadline for calls in seconds.
    callback: Optional callable, a callback triggered when this rpc
      completes; takes no arguments.
    read_policy: Optional read policy; set to EVENTUAL_CONSISTENCY to
      enable eventually consistent reads (i.e. reads that may be
      satisfied from an older version of the datastore in some cases).
      The default read policy may have to wait until in-flight
      transactions are committed.

  Returns:
    A UserRPC instance.
  """
  assert service == 'datastore_v3'
  conn = _GetConnection()
  config = None
  if deadline is not None:
    config = datastore_rpc.Configuration(deadline=deadline)
  rpc = conn.create_rpc(config)
  rpc.callback = callback
  if read_policy is not None:
    rpc.read_policy = read_policy
  return rpc


def CreateConfig(**kwds):
  """Create a Configuration object for use in configuring datastore calls.

  This configuration can be passed to most datastore calls using the
  'config=...' argument.

  Args:
    deadline: Optional deadline; default None (which means the
      system default deadline will be used, typically 5 seconds).
    on_completion: Optional callback function; default None.  If
      specified, it will be called with a UserRPC object as argument
      when an RPC completes.
    read_policy: Optional read policy; set to EVENTUAL_CONSISTENCY to
      enable eventually consistent reads (i.e. reads that may be
      satisfied from an older version of the datastore in some cases).
      The default read policy may have to wait until in-flight
      transactions are committed.
    **kwds: Other keyword arguments as long as they are supported by
      datastore_rpc.Configuration().

  Returns:
    A datastore_rpc.Configuration instance.
  """
  return datastore_rpc.Configuration(**kwds)


def _Rpc2Config(rpc):
  """Internal helper to construct a Configuration from a UserRPC object.

  If the argument is a UserRPC object, it returns a Configuration
  object constructed using the same deadline and read_policy;
  otherwise it returns the argument unchanged.

  NOTE: If the argument is a UserRPC object, its callback is *not*
  transferred to the Configuration object; the Configuration's
  on_completion attribute is set to None.  This is done because (a)
  the signature of on_completion differs from the callback signature;
  (b) the caller probably doesn't expect the callback to be called
  more than once; and (c) the callback, being argument-less, wouldn't
  know which UserRPC object was actually completing.  But yes,
  technically, this is a backwards incompatibility.

  Args:
    rpc: None, a UserRPC object, or a datastore_rpc.Configuration object.

  Returns:
    None or a datastore_rpc.Configuration object.
  """
  if rpc is None or isinstance(rpc, datastore_rpc.Configuration):
    return rpc
  read_policy = getattr(rpc, 'read_policy', None)
  return datastore_rpc.Configuration(deadline=rpc.deadline,
                                     read_policy=read_policy,
                                     config=_GetConnection().config)


def Put(entities, **kwargs):
  """Store one or more entities in the datastore.

  The entities may be new or previously existing. For new entities, Put() will
  fill in the app id and key assigned by the datastore.

  If the argument is a single Entity, a single Key will be returned. If the
  argument is a list of Entity, a list of Keys will be returned.

  Args:
    entities: Entity or list of Entities
    config: Optional Configuration to use for this request.

  Returns:
    Key or list of Keys

  Raises:
    TransactionFailedError, if the Put could not be committed.
  """
  config = _GetConfigFromKwargs(kwargs)
  if getattr(config, 'read_policy', None) == EVENTUAL_CONSISTENCY:
    raise datastore_errors.BadRequestError(
        'read_policy is only supported on read operations.')
  entities, multiple = NormalizeAndTypeCheck(entities, Entity)

  if multiple and not entities:
    return []

  for entity in entities:
    if not entity.kind() or not entity.app():
      raise datastore_errors.BadRequestError(
          'App and kind must not be empty, in entity: %s' % entity)

  def extra_hook(keys):
    num_keys = len(keys)
    num_entities = len(entities)
    if num_keys != num_entities:
      raise datastore_errors.InternalError(
          'Put accepted %d entities but returned %d keys.' %
          (num_entities, num_keys))

    for entity, key in zip(entities, keys):
      if entity._Entity__key._Key__reference != key._Key__reference:
        assert not entity._Entity__key.has_id_or_name()
        entity._Entity__key._Key__reference.CopyFrom(key._Key__reference)

    if multiple:
      return keys
    else:
      return keys[0]

  return _GetConnection().async_put(config, entities, extra_hook).get_result()


def Get(keys, **kwargs):
  """Retrieves one or more entities from the datastore.

  Retrieves the entity or entities with the given key(s) from the datastore
  and returns them as fully populated Entity objects, as defined below. If
  there is an error, raises a subclass of datastore_errors.Error.

  If keys is a single key or string, an Entity will be returned, or
  EntityNotFoundError will be raised if no existing entity matches the key.

  However, if keys is a list or tuple, a list of entities will be returned
  that corresponds to the sequence of keys. It will include entities for keys
  that were found and None placeholders for keys that were not found.

  Args:
    # the primary key(s) of the entity(ies) to retrieve
    keys: Key or string or list of Keys or strings
    config: Optional Configuration to use for this request.

  Returns:
    Entity or list of Entity objects
  """
  config = _GetConfigFromKwargs(kwargs)
  keys, multiple = NormalizeAndTypeCheckKeys(keys)

  if multiple and not keys:
    return []

  def extra_hook(entities):
    if multiple:
      return entities
    else:
      if entities[0] is None:
        raise datastore_errors.EntityNotFoundError()
      return entities[0]

  return _GetConnection().async_get(config, keys, extra_hook).get_result()


def Delete(keys, **kwargs):
  """Deletes one or more entities from the datastore. Use with care!

  Deletes the given entity(ies) from the datastore. You can only delete
  entities from your app. If there is an error, raises a subclass of
  datastore_errors.Error.

  Args:
    # the primary key(s) of the entity(ies) to delete
    keys: Key or string or list of Keys or strings
    config: Optional Configuration to use for this request.

  Raises:
    TransactionFailedError, if the Delete could not be committed.
  """
  config = _GetConfigFromKwargs(kwargs)
  if getattr(config, 'read_policy', None) == EVENTUAL_CONSISTENCY:
    raise datastore_errors.BadRequestError(
        'read_policy is only supported on read operations.')
  keys, multiple = NormalizeAndTypeCheckKeys(keys)

  if multiple and not keys:
    return

  _GetConnection().async_delete(config, keys).get_result()


class Entity(dict):
  """A datastore entity.

  Includes read-only accessors for app id, kind, and primary key. Also
  provides dictionary-style access to properties.
  """
  def __init__(self, kind, parent=None, _app=None, name=None, id=None,
               unindexed_properties=[], namespace=None, **kwds):
    """Constructor. Takes the kind and transaction root, which cannot be
    changed after the entity is constructed, and an optional parent. Raises
    BadArgumentError or BadKeyError if kind is invalid or parent is not an
    existing Entity or Key in the datastore.

    Args:
      # this entity's kind
      kind: string
      # if provided, this entity's parent. Its key must be complete.
      parent: Entity or Key
      # if provided, this entity's name.
      name: string
      # if provided, this entity's id.
      id: integer
      # if provided, a sequence of property names that should not be indexed
      # by the built-in single property indices.
      unindexed_properties: list or tuple of strings
      namespace: string
      # if provided, overrides the default namespace_manager setting.
    """





    ref = entity_pb.Reference()
    _app = datastore_types.ResolveAppId(_app)
    ref.set_app(_app)

    _namespace = kwds.pop('_namespace', None)

    if kwds:
      raise datastore_errors.BadArgumentError(
          'Excess keyword arguments ' + repr(kwds))




    if namespace is None:
      namespace = _namespace
    elif _namespace is not None:
        raise datastore_errors.BadArgumentError(
            "Must not set both _namespace and namespace parameters.")

    datastore_types.ValidateString(kind, 'kind',
                                   datastore_errors.BadArgumentError)

    if parent is not None:
      parent = _GetCompleteKeyOrError(parent)
      if _app != parent.app():
        raise datastore_errors.BadArgumentError(
            " %s doesn't match parent's app %s" %
            (_app, parent.app()))


      if namespace is None:
        namespace = parent.namespace()
      elif namespace != parent.namespace():
        raise datastore_errors.BadArgumentError(
            " %s doesn't match parent's namespace %s" %
            (namespace, parent.namespace()))
      ref.CopyFrom(parent._Key__reference)

    namespace = datastore_types.ResolveNamespace(namespace)
    datastore_types.SetNamespace(ref, namespace)

    last_path = ref.mutable_path().add_element()
    last_path.set_type(kind.encode('utf-8'))

    if name is not None and id is not None:
      raise datastore_errors.BadArgumentError(
          "Cannot set both name and id on an Entity")


    if name is not None:
      datastore_types.ValidateString(name, 'name')
      last_path.set_name(name.encode('utf-8'))

    if id is not None:
      datastore_types.ValidateInteger(id, 'id')
      last_path.set_id(id)

    self.set_unindexed_properties(unindexed_properties)

    self.__key = Key._FromPb(ref)

  def app(self):
    """Returns the name of the application that created this entity, a
    string or None if not set.
    """
    return self.__key.app()

  def namespace(self):
    """Returns the namespace of this entity, a string or None.
    """
    return self.__key.namespace()

  def kind(self):
    """Returns this entity's kind, a string.
    """
    return self.__key.kind()

  def is_saved(self):
    """Returns if this entity has been saved to the datastore
    """
    last_path = self.__key._Key__reference.path().element_list()[-1]
    return ((last_path.has_name() ^ last_path.has_id()) and
            self.__key.has_id_or_name())

  def key(self):
    """Returns this entity's primary key, a Key instance.
    """
    return self.__key

  def parent(self):
    """Returns this entity's parent, as a Key. If this entity has no parent,
    returns None.
    """
    return self.key().parent()

  def entity_group(self):
    """Returns this entity's entity group as a Key.

    Note that the returned Key will be incomplete if this is a a root entity
    and its key is incomplete.
    """
    return self.key().entity_group()

  def unindexed_properties(self):
    """Returns this entity's unindexed properties, as a frozenset of strings."""

    return getattr(self, '_Entity__unindexed_properties', [])

  def set_unindexed_properties(self, unindexed_properties):

    unindexed_properties, multiple = NormalizeAndTypeCheck(unindexed_properties, basestring)
    if not multiple:
      raise datastore_errors.BadArgumentError(
        'unindexed_properties must be a sequence; received %s (a %s).' %
        (unindexed_properties, typename(unindexed_properties)))
    for prop in unindexed_properties:
      datastore_types.ValidateProperty(prop, None)
    self.__unindexed_properties = frozenset(unindexed_properties)

  def __setitem__(self, name, value):
    """Implements the [] operator. Used to set property value(s).

    If the property name is the empty string or not a string, raises
    BadPropertyError. If the value is not a supported type, raises
    BadValueError.
    """

    datastore_types.ValidateProperty(name, value)
    dict.__setitem__(self, name, value)

  def setdefault(self, name, value):
    """If the property exists, returns its value. Otherwise sets it to value.

    If the property name is the empty string or not a string, raises
    BadPropertyError. If the value is not a supported type, raises
    BadValueError.
    """

    datastore_types.ValidateProperty(name, value)
    return dict.setdefault(self, name, value)

  def update(self, other):
    """Updates this entity's properties from the values in other.

    If any property name is the empty string or not a string, raises
    BadPropertyError. If any value is not a supported type, raises
    BadValueError.
    """
    for name, value in other.items():
      self.__setitem__(name, value)

  def copy(self):
    """The copy method is not supported.
    """
    raise NotImplementedError('Entity does not support the copy() method.')

  def ToXml(self):
    """Returns an XML representation of this entity. Atom and gd:namespace
    properties are converted to XML according to their respective schemas. For
    more information, see:

      http://www.atomenabled.org/developers/syndication/
      http://code.google.com/apis/gdata/common-elements.html

    This is *not* optimized. It shouldn't be used anywhere near code that's
    performance-critical.
    """

    xml = u'<entity kind=%s' % saxutils.quoteattr(self.kind())
    if self.__key.has_id_or_name():
      xml += ' key=%s' % saxutils.quoteattr(str(self.__key))
    xml += '>'
    if self.__key.has_id_or_name():
      xml += '\n  <key>%s</key>' % self.__key.ToTagUri()




    properties = self.keys()
    if properties:
      properties.sort()
      xml += '\n  ' + '\n  '.join(self._PropertiesToXml(properties))


    xml += '\n</entity>\n'
    return xml

  def _PropertiesToXml(self, properties):
    """ Returns a list of the XML representations of each of the given
    properties. Ignores properties that don't exist in this entity.

    Arg:
      properties: string or list of strings

    Returns:
      list of strings
    """
    xml_properties = []

    for propname in properties:
      if not self.has_key(propname):
        continue

      propname_xml = saxutils.quoteattr(propname)

      values = self[propname]
      if not isinstance(values, list):
        values = [values]

      proptype = datastore_types.PropertyTypeName(values[0])
      proptype_xml = saxutils.quoteattr(proptype)

      escaped_values = self._XmlEscapeValues(propname)
      open_tag = u'<property name=%s type=%s>' % (propname_xml, proptype_xml)
      close_tag = u'</property>'
      xml_properties += [open_tag + val + close_tag for val in escaped_values]

    return xml_properties

  def _XmlEscapeValues(self, property):
    """ Returns a list of the XML-escaped string values for the given property.
    Raises an AssertionError if the property doesn't exist.

    Arg:
      property: string

    Returns:
      list of strings
    """
    assert self.has_key(property)
    xml = []

    values = self[property]
    if not isinstance(values, list):
      values = [values]

    for val in values:
      if hasattr(val, 'ToXml'):
        xml.append(val.ToXml())
      else:
        if val is None:
          xml.append('')
        else:
          xml.append(saxutils.escape(unicode(val)))

    return xml

  def ToPb(self):
    """Converts this Entity to its protocol buffer representation.

    Returns:
      entity_pb.Entity
    """
    return self._ToPb(False)

  def _ToPb(self, mark_key_as_saved=True):
    """Converts this Entity to its protocol buffer representation. Not
    intended to be used by application developers.

    Returns:
      entity_pb.Entity
    """





    pb = entity_pb.EntityProto()
    pb.mutable_key().CopyFrom(self.key()._ToPb())
    last_path = pb.key().path().element_list()[-1]

    if mark_key_as_saved and last_path.has_name() and last_path.has_id():
      last_path.clear_id()


    group = pb.mutable_entity_group()
    if self.__key.has_id_or_name():
      root = pb.key().path().element(0)
      group.add_element().CopyFrom(root)


    properties = self.items()
    properties.sort()
    for (name, values) in properties:
      properties = datastore_types.ToPropertyPb(name, values)
      if not isinstance(properties, list):
        properties = [properties]

      for prop in properties:
        if (prop.meaning() in datastore_types._RAW_PROPERTY_MEANINGS or
            name in self.unindexed_properties()):
          pb.raw_property_list().append(prop)
        else:
          pb.property_list().append(prop)


    if pb.property_size() > _MAX_INDEXED_PROPERTIES:
      raise datastore_errors.BadRequestError(
          'Too many indexed properties for entity %r.' % self.key())

    return pb

  @staticmethod
  def FromPb(pb, validate_reserved_properties=True):
    """Static factory method. Returns the Entity representation of the
    given protocol buffer (datastore_pb.Entity).

    Args:
      pb: datastore_pb.Entity or str encoding of a datastore_pb.Entity

    Returns:
      Entity: the Entity representation of pb
    """
    if isinstance(pb, str):
      real_pb = entity_pb.EntityProto()
      real_pb.ParseFromString(pb)
      pb = real_pb

    return Entity._FromPb(
        pb, require_valid_key=False,
        validate_reserved_properties=validate_reserved_properties)

  @staticmethod
  def _FromPb(pb, require_valid_key=True, validate_reserved_properties=True):
    """Static factory method. Returns the Entity representation of the
    given protocol buffer (datastore_pb.Entity). Not intended to be used by
    application developers.

    The Entity PB's key must be complete. If it isn't, an AssertionError is
    raised.

    Args:
      # a protocol buffer Entity
      pb: datastore_pb.Entity

    Returns:
      # the Entity representation of the argument
      Entity
    """

    assert pb.key().path().element_size() > 0

    last_path = pb.key().path().element_list()[-1]
    if require_valid_key:
      assert last_path.has_id() ^ last_path.has_name()
      if last_path.has_id():
        assert last_path.id() != 0
      else:
        assert last_path.has_name()
        assert last_path.name()


    unindexed_properties = [p.name() for p in pb.raw_property_list()]


    if pb.key().has_name_space():
      namespace = pb.key().name_space()
    else:
      namespace = ''
    e = Entity(unicode(last_path.type().decode('utf-8')),
               unindexed_properties=unindexed_properties,
               _app=pb.key().app(), namespace=namespace)
    ref = e.__key._Key__reference
    ref.CopyFrom(pb.key())



    temporary_values = {}

    for prop_list in (pb.property_list(), pb.raw_property_list()):
      for prop in prop_list:
        try:
          value = datastore_types.FromPropertyPb(prop)
        except (AssertionError, AttributeError, TypeError, ValueError), e:
          raise datastore_errors.Error(
            'Property %s is corrupt in the datastore:\n%s' %
            (prop.name(), traceback.format_exc()))

        multiple = prop.multiple()
        if multiple:
          value = [value]

        name = prop.name()
        cur_value = temporary_values.get(name)
        if cur_value is None:
          temporary_values[name] = value
        elif not multiple or not isinstance(cur_value, list):
          raise datastore_errors.Error(
            'Property %s is corrupt in the datastore; it has multiple '
            'values, but is not marked as multiply valued.' % name)
        else:
          cur_value.extend(value)



    for name, value in temporary_values.iteritems():
      decoded_name = unicode(name.decode('utf-8'))




      datastore_types.ValidateReadProperty(
          decoded_name, value, read_only=(not validate_reserved_properties))

      dict.__setitem__(e, decoded_name, value)

    return e


class Query(dict):
  """A datastore query.

  (Instead of this, consider using appengine.ext.gql.Query! It provides a
  query language interface on top of the same functionality.)

  Queries are used to retrieve entities that match certain criteria, including
  app id, kind, and property filters. Results may also be sorted by properties.

  App id and kind are required. Only entities from the given app, of the given
  type, are returned. If an ancestor is set, with Ancestor(), only entities
  with that ancestor are returned.

  Property filters are used to provide criteria based on individual property
  values. A filter compares a specific property in each entity to a given
  value or list of possible values.

  An entity is returned if its property values match *all* of the query's
  filters. In other words, filters are combined with AND, not OR. If an
  entity does not have a value for a property used in a filter, it is not
  returned.

  Property filters map filter strings of the form '<property name> <operator>'
  to filter values. Use dictionary accessors to set property filters, like so:

  > query = Query('Person')
  > query['name ='] = 'Ryan'
  > query['age >='] = 21

  This query returns all Person entities where the name property is 'Ryan',
  'Ken', or 'Bret', and the age property is at least 21.

  Another way to build this query is:

  > query = Query('Person')
  > query.update({'name =': 'Ryan', 'age >=': 21})

  The supported operators are =, >, <, >=, and <=. Only one inequality
  filter may be used per query. Any number of equals filters may be used in
  a single Query.

  A filter value may be a list or tuple of values. This is interpreted as
  multiple filters with the same filter string and different values, all ANDed
  together. For example, this query returns everyone with the tags "google"
  and "app engine":

  > Query('Person', {'tag =': ('google', 'app engine')})

  Result entities can be returned in different orders. Use the Order()
  method to specify properties that results will be sorted by, and in which
  direction.

  Note that filters and orderings may be provided at any time before the query
  is run. When the query is fully specified, Run() runs the query and returns
  an iterator. The query results can be accessed through the iterator.

  A query object may be reused after it's been run. Its filters and
  orderings can be changed to create a modified query.

  If you know how many result entities you need, use Get() to fetch them:

  > query = Query('Person', {'age >': 21})
  > for person in query.Get(4):
  >   print 'I have four pints left. Have one on me, %s!' % person['name']

  If you don't know how many results you need, or if you need them all, you
  can get an iterator over the results by calling Run():

  > for person in Query('Person', {'age >': 21}).Run():
  >   print 'Have a pint on me, %s!' % person['name']

  Get() is more efficient than Run(), so use Get() whenever possible.

  Finally, the Count() method returns the number of result entities matched by
  the query. The returned count is cached; successive Count() calls will not
  re-scan the datastore unless the query is changed.
  """

  ASCENDING = datastore_query.PropertyOrder.ASCENDING
  DESCENDING = datastore_query.PropertyOrder.DESCENDING


  ORDER_FIRST = datastore_query.QueryOptions.ORDER_FIRST
  ANCESTOR_FIRST = datastore_query.QueryOptions.ANCESTOR_FIRST
  FILTER_FIRST = datastore_query.QueryOptions.FILTER_FIRST


  OPERATORS = {'==': datastore_query.PropertyFilter._OPERATORS['=']}
  OPERATORS.update(datastore_query.PropertyFilter._OPERATORS)

  INEQUALITY_OPERATORS = datastore_query.PropertyFilter._INEQUALITY_OPERATORS

  UPPERBOUND_INEQUALITY_OPERATORS = frozenset(['<', '<='])
  FILTER_REGEX = re.compile(
    '^\s*([^\s]+)(\s+(%s)\s*)?$' % '|'.join(OPERATORS),
    re.IGNORECASE | re.UNICODE)

  __kind = None
  __app = None
  __namespace = None
  __orderings = None
  __hint = None
  __ancestor_pb = None
  __compile = None


  __cursor = None

  __end_cursor = None




  __filter_order = None
  __filter_counter = 0


  __inequality_prop = None
  __inequality_count = 0

  def __init__(self, kind=None, filters={}, _app=None, keys_only=False,
               compile=True, cursor=None, namespace=None, end_cursor=None,
               **kwds):
    """Constructor.

    Raises BadArgumentError if kind is not a string. Raises BadValueError or
    BadFilterError if filters is not a dictionary of valid filters.

    Args:
      # kind is required. filters is optional; if provided, it's used
      # as an initial set of property filters. keys_only defaults to False.
      kind: string
      filters: dict
      keys_only: boolean
      namespace: string
    """






    _namespace = kwds.pop('_namespace', None)

    if kwds:
      raise datastore_errors.BadArgumentError(
          'Excess keyword arguments ' + repr(kwds))




    if namespace is None:
      namespace = _namespace
    elif _namespace is not None:
        raise datastore_errors.BadArgumentError(
            "Must not set both _namespace and namespace parameters.")

    if kind is not None:
      datastore_types.ValidateString(kind, 'kind',
                                     datastore_errors.BadArgumentError)

    self.__kind = kind
    self.__orderings = []
    self.__filter_order = {}
    self.update(filters)

    self.__app = datastore_types.ResolveAppId(_app)
    self.__namespace = datastore_types.ResolveNamespace(namespace)
    self.__keys_only = keys_only
    self.__compile = compile
    self.__cursor = cursor
    self.__end_cursor = end_cursor

  def Order(self, *orderings):
    """Specify how the query results should be sorted.

    Result entities will be sorted by the first property argument, then by the
    second, and so on. For example, this:

    > query = Query('Person')
    > query.Order('bday', ('age', Query.DESCENDING))

    sorts everyone in order of their birthday, starting with January 1.
    People with the same birthday are sorted by age, oldest to youngest.

    The direction for each sort property may be provided; if omitted, it
    defaults to ascending.

    Order() may be called multiple times. Each call resets the sort order
    from scratch.

    If an inequality filter exists in this Query it must be the first property
    passed to Order. Any number of sort orders may be used after the
    inequality filter property. Without inequality filters, any number of
    filters with different orders may be specified.

    Entities with multiple values for an order property are sorted by their
    lowest value.

    Note that a sort order implies an existence filter! In other words,
    Entities without the sort order property are filtered out, and *not*
    included in the query results.

    If the sort order property has different types in different entities - ie,
    if bob['id'] is an int and fred['id'] is a string - the entities will be
    grouped first by the property type, then sorted within type. No attempt is
    made to compare property values across types.

    Raises BadArgumentError if any argument is of the wrong format.

    Args:
      # the properties to sort by, in sort order. each argument may be either a
      # string or (string, direction) 2-tuple.

    Returns:
      # this query
      Query
    """
    orderings = list(orderings)


    for (order, i) in zip(orderings, range(len(orderings))):
      if not (isinstance(order, basestring) or
              (isinstance(order, tuple) and len(order) in [2, 3])):
        raise datastore_errors.BadArgumentError(
          'Order() expects strings or 2- or 3-tuples; received %s (a %s). ' %
          (order, typename(order)))


      if isinstance(order, basestring):
        order = (order,)

      datastore_types.ValidateString(order[0], 'sort order property',
                                     datastore_errors.BadArgumentError)
      property = order[0]


      direction = order[-1]
      if direction not in (Query.ASCENDING, Query.DESCENDING):
        if len(order) == 3:
          raise datastore_errors.BadArgumentError(
            'Order() expects Query.ASCENDING or DESCENDING; received %s' %
            str(direction))

        direction = Query.ASCENDING

      if (self.__kind is None and
          (property != datastore_types._KEY_SPECIAL_PROPERTY or
          direction != Query.ASCENDING)):
        raise datastore_errors.BadArgumentError(
            'Only %s ascending orders are supported on kindless queries' %
            datastore_types._KEY_SPECIAL_PROPERTY)

      orderings[i] = (property, direction)


    if (orderings and self.__inequality_prop and
        orderings[0][0] != self.__inequality_prop):
      raise datastore_errors.BadArgumentError(
        'First ordering property must be the same as inequality filter '
        'property, if specified for this query; received %s, expected %s' %
        (orderings[0][0], self.__inequality_prop))

    self.__orderings = orderings
    return self

  def Hint(self, hint):
    """Sets a hint for how this query should run.

    The query hint gives us information about how best to execute your query.
    Currently, we can only do one index scan, so the query hint should be used
    to indicates which index we should scan against.

    Use FILTER_FIRST if your first filter will only match a few results. In
    this case, it will be most efficient to scan against the index for this
    property, load the results into memory, and apply the remaining filters
    and sort orders there.

    Similarly, use ANCESTOR_FIRST if the query's ancestor only has a few
    descendants. In this case, it will be most efficient to scan all entities
    below the ancestor and load them into memory first.

    Use ORDER_FIRST if the query has a sort order and the result set is large
    or you only plan to fetch the first few results. In that case, we
    shouldn't try to load all of the results into memory; instead, we should
    scan the index for this property, which is in sorted order.

    Note that hints are currently ignored in the v3 datastore!

    Arg:
      one of datastore.Query.[ORDER_FIRST, ANCESTOR_FIRST, FILTER_FIRST]

    Returns:
      # this query
      Query
    """
    if hint not in [self.ORDER_FIRST, self.ANCESTOR_FIRST, self.FILTER_FIRST]:
      raise datastore_errors.BadArgumentError(
        'Query hint must be ORDER_FIRST, ANCESTOR_FIRST, or FILTER_FIRST.')

    self.__hint = hint
    return self

  def Ancestor(self, ancestor):
    """Sets an ancestor for this query.

    This restricts the query to only return result entities that are descended
    from a given entity. In other words, all of the results will have the
    ancestor as their parent, or parent's parent, or etc.

    Raises BadArgumentError or BadKeyError if parent is not an existing Entity
    or Key in the datastore.

    Args:
      # the key must be complete
      ancestor: Entity or Key

    Returns:
      # this query
      Query
    """
    self.__ancestor_pb = _GetCompleteKeyOrError(ancestor)._ToPb()
    return self

  def IsKeysOnly(self):
    """Returns True if this query is keys only, false otherwise."""
    return self.__keys_only

  def GetQueryOptions(self):
    """Returns a datastore_query.QueryOptions for the current instance."""
    return datastore_query.QueryOptions(keys_only=self.__keys_only,
                                        produce_cursors=self.__compile,
                                        start_cursor=self.__cursor,
                                        end_cursor=self.__end_cursor,
                                        hint=self.__hint)

  def GetQuery(self):
    """Returns a datastore_query.Query for the current instance."""
    return datastore_query.Query(app=self.__app,
                                 namespace=self.__namespace,
                                 kind=self.__kind,
                                 ancestor=self.__ancestor_pb,
                                 filter_predicate=self.GetFilterPredicate(),
                                 order=self.GetOrder())

  def GetOrder(self):
    """Gets a datastore_query.Order for the current instance.

    Returns:
      datastore_query.Order or None if there are no sort orders set on the
      current Query.
    """


    orders = [datastore_query.PropertyOrder(property, direction)
              for property, direction in self.__orderings]
    if orders:
      return datastore_query.CompositeOrder(orders)
    return None

  def GetFilterPredicate(self):
    """Returns a datastore_query.FilterPredicate for the current instance.

    Returns:
      datastore_query.FilterPredicate or None if no filters are set on the
      current Query.
    """

    ordered_filters = [(i, f) for f, i in self.__filter_order.iteritems()]
    ordered_filters.sort()

    property_filters = []
    for _, filter_str in ordered_filters:
      if filter_str not in self:

        continue

      values = self[filter_str]
      match = self._CheckFilter(filter_str, values)
      name = match.group(1)

      op = match.group(3)
      if op is None or op == '==':

        op = '='

      property_filters.append(datastore_query.make_filter(name, op, values))

    if property_filters:
      return datastore_query.CompositeFilter(
          datastore_query.CompositeFilter.AND,
          property_filters)
    return None

  def GetCursor(self):
    """Get the cursor from the last run of this query.

    The source of this cursor varies depending on what the last call was:
      - Run: A cursor that points immediately after the last result pulled off
        the returned iterator.
      - Get: A cursor that points immediately after the last result in the
        returned list.
      - Count: A cursor that points immediately after the last result counted.

    Returns:
      A datastore_query.Cursor object that can be used in subsiquent query
      requests.
    """
    try:


      cursor = self.__cursor_source()
      if not cursor:
        raise AttributeError()
    except AttributeError:
      raise AssertionError('No cursor available, either this query has not '
                           'been executed or there is no compilation '
                           'available for this kind of query')
    return cursor

  def GetBatcher(self, config=None):
    """Runs this query and returns a datastore_query.Batcher.

    This is not intended to be used by application developers. Use Get()
    instead!

    Args:
      config: Optional Configuration to use for this request.

    Returns:
      # an iterator that provides access to the query results
      Iterator
    """


    query_options = self.GetQueryOptions().merge(config)
    return self.GetQuery().run(_GetConnection(), query_options)

  def Run(self, **kwargs):
    """Runs this query.

    If a filter string is invalid, raises BadFilterError. If a filter value is
    invalid, raises BadValueError. If an IN filter is provided, and a sort
    order on another property is provided, raises BadQueryError.

    If you know in advance how many results you want, use Get() instead. It's
    more efficient.

    Args:
      config: Optional Configuration to use for this request.

    Returns:
      # an iterator that provides access to the query results
      Iterator
    """
    config = _Rpc2Config(_GetConfigFromKwargs(kwargs))
    itr = Iterator(self.GetBatcher(config=config))

    self.__cursor_source = itr.cursor

    self.__compiled_query_source = itr._compiled_query
    return itr

  def Get(self, limit, offset=0, **kwargs):
    """Fetches and returns a maximum number of results from the query.

    This method fetches and returns a list of resulting entities that matched
    the query. If the query specified a sort order, entities are returned in
    that order. Otherwise, the order is undefined.

    The limit argument specifies the maximum number of entities to return. If
    it's greater than the number of remaining entities, all of the remaining
    entities are returned. In that case, the length of the returned list will
    be smaller than limit.

    The offset argument specifies the number of entities that matched the
    query criteria to skip before starting to return results.  The limit is
    applied after the offset, so if you provide a limit of 10 and an offset of 5
    and your query matches 20 records, the records whose index is 0 through 4
    will be skipped and the records whose index is 5 through 14 will be
    returned.

    The results are always returned as a list. If there are no results left,
    an empty list is returned.

    If you know in advance how many results you want, this method is more
    efficient than Run(), since it fetches all of the results at once. (The
    datastore backend sets the the limit on the underlying
    scan, which makes the scan significantly faster.)

    Args:
      # the maximum number of entities to return
      int or long
      # the number of entities to skip
      int or long
      config: Optional Configuration to use for this request. If limit and
      offset are specified in the config, they are ignored.

    Returns:
      # a list of entities
      [Entity, ...]
    """
    config = _Rpc2Config(_GetConfigFromKwargs(kwargs))
    batcher = self.GetBatcher(datastore_query.QueryOptions(
        config=config, limit=limit, offset=offset, prefetch_size=limit))

    if limit is None:
      batch = batcher.next_batch(_MAX_INT_32)
    else:
      batch = batcher.next_batch(limit)
    self.__cursor_source = lambda: batch.end_cursor
    self.__compiled_query_source = lambda: batch._compiled_query
    return batch.results

  def Count(self, limit=1000, **kwargs):
    """Returns the number of entities that this query matches.

    Args:
      limit, a number or None. If there are more results than this, stop short
      and just return this number. Providing this argument makes the count
      operation more efficient.
      config: Optional Configuration to use for this request.

    Returns:
      The number of results.
    """
    if limit is None:
      offset = _MAX_INT_32
    else:
      offset = limit

    config = datastore_query.QueryOptions(
        config=_Rpc2Config(_GetConfigFromKwargs(kwargs)),
        limit=0,
        offset=offset)

    batch = self.GetBatcher(config=config).next()
    self.__cursor_source = lambda: batch.cursor(0)
    self.__compiled_query_source = lambda: batch._compiled_query
    return batch.skipped_results

  def __iter__(self):
    raise NotImplementedError(
      'Query objects should not be used as iterators. Call Run() first.')

  def __getstate__(self):
    state = self.__dict__.copy()
    if '_Query__cursor_source' in state:
      del state['_Query__cursor_source']
    if '_Query__compiled_query_source' in state:
      del state['_Query__compiled_query_source']
    return state

  def __setitem__(self, filter, value):
    """Implements the [] operator. Used to set filters.

    If the filter string is empty or not a string, raises BadFilterError. If
    the value is not a supported type, raises BadValueError.
    """
    if isinstance(value, tuple):
      value = list(value)

    datastore_types.ValidateProperty(' ', value, read_only=True)
    match = self._CheckFilter(filter, value)
    property = match.group(1)
    operator = match.group(3)

    dict.__setitem__(self, filter, value)

    if (operator in self.INEQUALITY_OPERATORS and
        property != datastore_types._UNAPPLIED_LOG_TIMESTAMP_SPECIAL_PROPERTY):

      if self.__inequality_prop is None:
        self.__inequality_prop = property
      else:
        assert self.__inequality_prop == property
      self.__inequality_count += 1


    if filter not in self.__filter_order:
      self.__filter_order[filter] = self.__filter_counter
      self.__filter_counter += 1

  def setdefault(self, filter, value):
    """If the filter exists, returns its value. Otherwise sets it to value.

    If the property name is the empty string or not a string, raises
    BadPropertyError. If the value is not a supported type, raises
    BadValueError.
    """
    datastore_types.ValidateProperty(' ', value)
    self._CheckFilter(filter, value)
    return dict.setdefault(self, filter, value)

  def __delitem__(self, filter):
    """Implements the del [] operator. Used to remove filters.
    """
    dict.__delitem__(self, filter)
    del self.__filter_order[filter]


    match = Query.FILTER_REGEX.match(filter)
    property = match.group(1)
    operator = match.group(3)

    if operator in self.INEQUALITY_OPERATORS:
      assert self.__inequality_count >= 1
      assert property == self.__inequality_prop
      self.__inequality_count -= 1
      if self.__inequality_count == 0:
        self.__inequality_prop = None

  def update(self, other):
    """Updates this query's filters from the ones in other.

    If any filter string is invalid, raises BadFilterError. If any value is
    not a supported type, raises BadValueError.
    """
    for filter, value in other.items():
      self.__setitem__(filter, value)

  def copy(self):
    """The copy method is not supported.
    """
    raise NotImplementedError('Query does not support the copy() method.')

  def _CheckFilter(self, filter, values):
    """Type check a filter string and list of values.

    Raises BadFilterError if the filter string is empty, not a string, or
    invalid. Raises BadValueError if the value type is not supported.

    Args:
      filter: String containing the filter text.
      values: List of associated filter values.

    Returns:
      re.MatchObject (never None) that matches the 'filter'. Group 1 is the
      property name, group 3 is the operator. (Group 2 is unused.)
    """
    try:
      match = Query.FILTER_REGEX.match(filter)
      if not match:
        raise datastore_errors.BadFilterError(
          'Could not parse filter string: %s' % str(filter))
    except TypeError:
      raise datastore_errors.BadFilterError(
        'Could not parse filter string: %s' % str(filter))

    property = match.group(1)
    operator = match.group(3)
    if operator is None:
      operator = '='

    if isinstance(values, tuple):
      values = list(values)
    elif not isinstance(values, list):
      values = [values]
    if isinstance(values[0], datastore_types._RAW_PROPERTY_TYPES):
      raise datastore_errors.BadValueError(
        'Filtering on %s properties is not supported.' % typename(values[0]))

    if (operator in self.INEQUALITY_OPERATORS and
        property != datastore_types._UNAPPLIED_LOG_TIMESTAMP_SPECIAL_PROPERTY):
      if self.__inequality_prop and property != self.__inequality_prop:
        raise datastore_errors.BadFilterError(
            'Only one property per query may have inequality filters (%s).' %
            ', '.join(self.INEQUALITY_OPERATORS))
      elif len(self.__orderings) >= 1 and self.__orderings[0][0] != property:
        raise datastore_errors.BadFilterError(
            'Inequality operators (%s) must be on the same property as the '
            'first sort order, if any sort orders are supplied' %
            ', '.join(self.INEQUALITY_OPERATORS))

    if (self.__kind is None and
        property != datastore_types._KEY_SPECIAL_PROPERTY and
        property != datastore_types._UNAPPLIED_LOG_TIMESTAMP_SPECIAL_PROPERTY):
      raise datastore_errors.BadFilterError(
          'Only %s filters are allowed on kindless queries.' %
          datastore_types._KEY_SPECIAL_PROPERTY)

    if property == datastore_types._UNAPPLIED_LOG_TIMESTAMP_SPECIAL_PROPERTY:
      if self.__kind:
        raise datastore_errors.BadFilterError(
            'Only kindless queries can have %s filters.' %
            datastore_types._UNAPPLIED_LOG_TIMESTAMP_SPECIAL_PROPERTY)
      if not operator in self.UPPERBOUND_INEQUALITY_OPERATORS:
        raise datastore_errors.BadFilterError(
            'Only %s operators are supported with %s filters.' % (
            self.UPPERBOUND_INEQUALITY_OPERATORS,
            datastore_types._UNAPPLIED_LOG_TIMESTAMP_SPECIAL_PROPERTY))

    if property in datastore_types._SPECIAL_PROPERTIES:




      if property == datastore_types._KEY_SPECIAL_PROPERTY:
        for value in values:
          if not isinstance(value, Key):
            raise datastore_errors.BadFilterError(
              '%s filter value must be a Key; received %s (a %s)' %
              (datastore_types._KEY_SPECIAL_PROPERTY, value, typename(value)))

    return match

  def _Run(self, limit=None, offset=None,
           prefetch_count=None, next_count=None, **kwargs):
    """Deprecated, use .Run instead."""
    config = _Rpc2Config(_GetConfigFromKwargs(kwargs))
    return self.Run(config=datastore_query.QueryOptions(
        config=config,
        limit=limit,
        offset=offset,
        prefetch_size=prefetch_count,
        batch_size=next_count))

  def _ToPb(self, limit=None, offset=None, count=None):

    query_options = datastore_query.QueryOptions(
        config=self.GetQueryOptions(),
        limit=limit,
        offset=offset,
        batch_size=count)
    return self.GetQuery()._to_pb(_GetConnection(), query_options)

  def _GetCompiledQuery(self):
    """Returns the internal-only pb representation of the last query run.

    Do not use.
    """
    try:


      compiled_query = self.__compiled_query_source()
      if not compiled_query:
        raise AttributeError()
    except AttributeError:
      raise AssertionError('No compiled query available, either this query has '
                           'not been executed or there is no compilation '
                           'available for this kind of query')
    return compiled_query

  GetCompiledQuery = _GetCompiledQuery
  GetCompiledCursor = GetCursor


def AllocateIds(model_key, size=None, **kwargs):
  """Allocates a range of IDs of size or with max for the given key.

  Allocates a range of IDs in the datastore such that those IDs will not
  be automatically assigned to new entities. You can only allocate IDs
  for model keys from your app. If there is an error, raises a subclass of
  datastore_errors.Error.

  Either size or max must be provided but not both. If size is provided then a
  range of the given size is returned. If max is provided then the largest
  range of ids that are safe to use with an upper bound of max is returned (can
  be an empty range).

  Max should only be provided if you have an existing numeric id range that you
  want to reserve, e.g. bulk loading entities that already have IDs. If you
  don't care about which IDs you receive, use size instead.

  Args:
    model_key: Key or string to serve as a model specifying the ID sequence
               in which to allocate IDs
    size: integer, number of IDs to allocate.
    max: integer, upper bound of the range of IDs to allocate.
    config: Optional Configuration to use for this request.

  Returns:
    (start, end) of the allocated range, inclusive.
  """
  max = kwargs.pop('max', None)
  config = _GetConfigFromKwargs(kwargs)
  if getattr(config, 'read_policy', None) == EVENTUAL_CONSISTENCY:
    raise datastore_errors.BadRequestError(
        'read_policy is only supported on read operations.')
  keys, _ = NormalizeAndTypeCheckKeys(model_key)

  if len(keys) > 1:
    raise datastore_errors.BadArgumentError(
        'Cannot allocate IDs for more than one model key at a time')

  rpc = _GetConnection().async_allocate_ids(config, keys[0], size, max)
  return rpc.get_result()




class MultiQuery(Query):
  """Class representing a query which requires multiple datastore queries.

  This class is actually a subclass of datastore.Query as it is intended to act
  like a normal Query object (supporting the same interface).

  Does not support keys only queries, since it needs whole entities in order
  to merge sort them. (That's not true if there are no sort orders, or if the
  sort order is on __key__, but allowing keys only queries in those cases, but
  not in others, would be confusing.)
  """

  def __init__(self, bound_queries, orderings):
    if len(bound_queries) > MAX_ALLOWABLE_QUERIES:
      raise datastore_errors.BadArgumentError(
          'Cannot satisfy query -- too many subqueries (max: %d, got %d).'
          ' Probable cause: too many IN/!= filters in query.' %
          (MAX_ALLOWABLE_QUERIES, len(bound_queries)))

    for query in bound_queries:
      if query.IsKeysOnly():
        raise datastore_errors.BadQueryError(
            'MultiQuery does not support keys_only.')

    self.__bound_queries = bound_queries
    self.__orderings = orderings
    self.__compile = False

  def __str__(self):
    res = 'MultiQuery: '
    for query in self.__bound_queries:
      res = '%s %s' % (res, str(query))
    return res

  def Get(self, limit, offset=0, **kwargs):
    """Get results of the query with a limit on the number of results.

    Args:
      limit: maximum number of values to return.
      offset: offset requested -- if nonzero, this will override the offset in
              the original query
      config: Optional Configuration to use for this request.

    Returns:
      A list of entities with at most "limit" entries (less if the query
      completes before reading limit values).
    """
    config = _GetConfigFromKwargs(kwargs)
    count = 1
    result = []




    iterator = self.Run(config=config)


    try:
      for i in xrange(offset):
        val = iterator.next()
    except StopIteration:
      pass


    try:
      while count <= limit:
        val = iterator.next()
        result.append(val)
        count += 1
    except StopIteration:
      pass
    return result

  class SortOrderEntity(object):
    """Allow entity comparisons using provided orderings.

    The iterator passed to the constructor is eventually consumed via
    calls to GetNext(), which generate new SortOrderEntity s with the
    same orderings.
    """

    def __init__(self, entity_iterator, orderings):
      """Ctor.

      Args:
        entity_iterator: an iterator of entities which will be wrapped.
        orderings: an iterable of (identifier, order) pairs. order
          should be either Query.ASCENDING or Query.DESCENDING.
      """
      self.__entity_iterator = entity_iterator
      self.__entity = None
      self.__min_max_value_cache = {}
      try:
        self.__entity = entity_iterator.next()
      except StopIteration:
        pass
      else:
        self.__orderings = orderings

    def __str__(self):
      return str(self.__entity)

    def GetEntity(self):
      """Gets the wrapped entity."""
      return self.__entity

    def GetNext(self):
      """Wrap and return the next entity.

      The entity is retrieved from the iterator given at construction time.
      """
      return MultiQuery.SortOrderEntity(self.__entity_iterator,
                                        self.__orderings)

    def CmpProperties(self, that):
      """Compare two entities and return their relative order.

      Compares self to that based on the current sort orderings and the
      key orders between them. Returns negative, 0, or positive depending on
      whether self is less, equal to, or greater than that. This
      comparison returns as if all values were to be placed in ascending order
      (highest value last).  Only uses the sort orderings to compare (ignores
       keys).

      Args:
        that: SortOrderEntity

      Returns:
        Negative if self < that
        Zero if self == that
        Positive if self > that
      """

      if not self.__entity:
        return cmp(self.__entity, that.__entity)


      for (identifier, order) in self.__orderings:

        value1 = self.__GetValueForId(self, identifier, order)
        value2 = self.__GetValueForId(that, identifier, order)

        result = cmp(value1, value2)
        if order == Query.DESCENDING:
          result = -result
        if result:
          return result
      return 0

    def __GetValueForId(self, sort_order_entity, identifier, sort_order):



      value = _GetPropertyValue(sort_order_entity.__entity, identifier)
      if isinstance(value, list):
        entity_key = sort_order_entity.__entity.key()
        if (entity_key, identifier) in self.__min_max_value_cache:
          value = self.__min_max_value_cache[(entity_key, identifier)]
        elif sort_order == Query.DESCENDING:
          value = min(value)
        else:
          value = max(value)
        self.__min_max_value_cache[(entity_key, identifier)] = value

      return value

    def __cmp__(self, that):
      """Compare self to that w.r.t. values defined in the sort order.

      Compare an entity with another, using sort-order first, then the key
      order to break ties. This can be used in a heap to have faster min-value
      lookup.

      Args:
        that: other entity to compare to
      Returns:
        negative: if self is less than that in sort order
        zero: if self is equal to that in sort order
        positive: if self is greater than that in sort order
      """
      property_compare = self.CmpProperties(that)
      if property_compare:
        return property_compare
      else:

        return cmp(self.__entity.key(), that.__entity.key())

  def Run(self, **kwargs):
    """Return an iterable output with all results in order.

    Merge sort the results. First create a list of iterators, then walk
    though them and yield results in order.
    """
    config = _GetConfigFromKwargs(kwargs)
    config = _Rpc2Config(config)
    results = []
    count = 1
    log_level = logging.DEBUG - 1
    for bound_query in self.__bound_queries:
      logging.log(log_level, 'Running query #%i' % count)
      results.append(bound_query.Run(config=config))
      count += 1

    def IterateResults(results):
      """Iterator function to return all results in sorted order.

      Iterate over the array of results, yielding the next element, in
      sorted order. This function is destructive (results will be empty
      when the operation is complete).

      Args:
        results: list of result iterators to merge and iterate through

      Yields:
        The next result in sorted order.
      """


      result_heap = []
      for result in results:
        heap_value = MultiQuery.SortOrderEntity(result, self.__orderings)
        if heap_value.GetEntity():
          heapq.heappush(result_heap, heap_value)





      used_keys = set()


      while result_heap:
        top_result = heapq.heappop(result_heap)

        results_to_push = []
        if top_result.GetEntity().key() not in used_keys:
          yield top_result.GetEntity()
        else:

          pass

        used_keys.add(top_result.GetEntity().key())


        results_to_push = []
        while result_heap:
          next = heapq.heappop(result_heap)
          if cmp(top_result, next):

            results_to_push.append(next)
            break
          else:


            results_to_push.append(next.GetNext())
        results_to_push.append(top_result.GetNext())


        for popped_result in results_to_push:


          if popped_result.GetEntity():
            heapq.heappush(result_heap, popped_result)

    return IterateResults(results)

  def Count(self, limit=None, **kwargs):
    """Return the number of matched entities for this query.

    Will return the de-duplicated count of results.  Will call the more
    efficient Get() function if a limit is given.

    Args:
      limit: maximum number of entries to count (for any result > limit, return
      limit).
      config: Optional Configuration to use for this request.

    Returns:
      count of the number of entries returned.
    """


    config = _GetConfigFromKwargs(kwargs)
    if limit is None:




      count = 0
      for _ in self.Run(config=config):
        count += 1
      return count
    else:


      return len(self.Get(limit, config=config))

  def GetCursor(self):
    raise AssertionError('No cursor available for a MultiQuery (queries '
                         'using "IN" or "!=" operators)')


  def _GetCompiledQuery(self):
    """Internal only, do not use."""
    raise AssertionError('No compilation available for a MultiQuery (queries '
                         'using "IN" or "!=" operators)')

  def __setitem__(self, query_filter, value):
    """Add a new filter by setting it on all subqueries.

    If any of the setting operations raise an exception, the ones
    that succeeded are undone and the exception is propagated
    upward.

    Args:
      query_filter: a string of the form "property operand".
      value: the value that the given property is compared against.
    """
    saved_items = []
    for index, query in enumerate(self.__bound_queries):
      saved_items.append(query.get(query_filter, None))
      try:
        query[query_filter] = value
      except:
        for q, old_value in itertools.izip(self.__bound_queries[:index],
                                           saved_items):
          if old_value is not None:
            q[query_filter] = old_value
          else:
            del q[query_filter]
        raise

  def __delitem__(self, query_filter):
    """Delete a filter by deleting it from all subqueries.

    If a KeyError is raised during the attempt, it is ignored, unless
    every subquery raised a KeyError. If any other exception is
    raised, any deletes will be rolled back.

    Args:
      query_filter: the filter to delete.

    Raises:
      KeyError: No subquery had an entry containing query_filter.
    """
    subquery_count = len(self.__bound_queries)
    keyerror_count = 0
    saved_items = []
    for index, query in enumerate(self.__bound_queries):
      try:
        saved_items.append(query.get(query_filter, None))
        del query[query_filter]
      except KeyError:
        keyerror_count += 1
      except:
        for q, old_value in itertools.izip(self.__bound_queries[:index],
                                           saved_items):
          if old_value is not None:
            q[query_filter] = old_value
        raise

    if keyerror_count == subquery_count:
      raise KeyError(query_filter)

  def __iter__(self):
    return iter(self.__bound_queries)


  GetCompiledCursor = GetCursor
  GetCompiledQuery = _GetCompiledQuery


def RunInTransaction(function, *args, **kwargs):
  """Runs a function inside a datastore transaction.

     Runs the user-provided function inside transaction, retries default
     number of times.

    Args:
    # a function to be run inside the transaction
    function: callable
    # positional arguments to pass to the function
    args: variable number of any type

  Returns:
    the function's return value, if any

  Raises:
    TransactionFailedError, if the transaction could not be committed.
  """
  return RunInTransactionCustomRetries(
      DEFAULT_TRANSACTION_RETRIES, function, *args, **kwargs)





def RunInTransactionCustomRetries(retries, function, *args, **kwargs):
  """Runs a function inside a datastore transaction.

  Runs the user-provided function inside a full-featured, ACID datastore
  transaction. Every Put, Get, and Delete call in the function is made within
  the transaction. All entities involved in these calls must belong to the
  same entity group. Queries are supported as long as they specify an
  ancestor belonging to the same entity group.

  The trailing arguments are passed to the function as positional arguments.
  If the function returns a value, that value will be returned by
  RunInTransaction. Otherwise, it will return None.

  The function may raise any exception to roll back the transaction instead of
  committing it. If this happens, the transaction will be rolled back and the
  exception will be re-raised up to RunInTransaction's caller.

  If you want to roll back intentionally, but don't have an appropriate
  exception to raise, you can raise an instance of datastore_errors.Rollback.
  It will cause a rollback, but will *not* be re-raised up to the caller.

  The function may be run more than once, so it should be idempotent. It
  should avoid side effects, and it shouldn't have *any* side effects that
  aren't safe to occur multiple times. This includes modifying the arguments,
  since they persist across invocations of the function. However, this doesn't
  include Put, Get, and Delete calls, of course.

  Example usage:

  > def decrement(key, amount=1):
  >   counter = datastore.Get(key)
  >   counter['count'] -= amount
  >   if counter['count'] < 0:    # don't let the counter go negative
  >     raise datastore_errors.Rollback()
  >   datastore.Put(counter)
  >
  > counter = datastore.Query('Counter', {'name': 'foo'})
  > datastore.RunInTransaction(decrement, counter.key(), amount=5)

  Transactions satisfy the traditional ACID properties. They are:

  - Atomic. All of a transaction's operations are executed or none of them are.

  - Consistent. The datastore's state is consistent before and after a
  transaction, whether it committed or rolled back. Invariants such as
  "every entity has a primary key" are preserved.

  - Isolated. Transactions operate on a snapshot of the datastore. Other
  datastore operations do not see intermediated effects of the transaction;
  they only see its effects after it has committed.

  - Durable. On commit, all writes are persisted to the datastore.

  Nested transactions are not supported.

  Args:
    # number of retries (not counting the initial try)
    retries: integer
    # a function to be run inside the transaction
    function: callable
    # positional arguments to pass to the function
    args: variable number of any type

  Returns:
    the function's return value, if any

  Raises:
    TransactionFailedError, if the transaction could not be committed.
  """









  if retries < 0:
    raise datastore_errors.BadRequestError(
      'Number of retries should be non-negative number.')


  if IsInTransaction():
    raise datastore_errors.BadRequestError(
      'Nested transactions are not supported.')

  old_connection = _GetConnection()

  for i in range(0, retries + 1):
    new_connection = old_connection.new_transaction()
    _SetConnection(new_connection)
    try:
      ok, result = _DoOneTry(new_connection, function, args, kwargs)
      if ok:
        return result
    finally:
      _SetConnection(old_connection)


  raise datastore_errors.TransactionFailedError(
    'The transaction could not be committed. Please try again.')


def _DoOneTry(new_connection, function, args, kwargs):
  """Helper to call a function in a transaction, once.

  Args:
    new_connection: The new, transactional, connection object.
    function: The function to call.
    args: Tuple of positional arguments.
    kwargs: Dict of keyword arguments.
  """

  try:
    result = function(*args, **kwargs)

  except:
    original_exception = sys.exc_info()

    try:
      new_connection.rollback()
    except Exception:



      logging.exception('Exception sending Rollback:')

    type, value, trace = original_exception
    if isinstance(value, datastore_errors.Rollback):
      return True, None
    else:
      raise type, value, trace

  else:
    if new_connection.commit():
      return True, result
    else:


      logging.warning('Transaction collision. Retrying... %s', '')
      return False, None


def _MaybeSetupTransaction(request, keys):
  """Begin a transaction, if necessary, and populate it in the request.

  This API exists for internal backwards compatibility, primarily with
  api/taskqueue/taskqueue.py.

  Args:
    request: A protobuf with a mutable_transaction() method.
    keys: Unused.

  Returns:
    A transaction if we're inside a transaction, otherwise None
  """
  return _GetConnection()._set_request_transaction(request)


def IsInTransaction():
  """Determine whether already running in transaction.

  Returns:
    True if already running in transaction, else False.
  """

  return isinstance(_GetConnection(), datastore_rpc.TransactionalConnection)


def _GetCompleteKeyOrError(arg):
  """Expects an Entity or a Key, and returns the corresponding Key. Raises
  BadArgumentError or BadKeyError if arg is a different type or is incomplete.

  Args:
    arg: Entity or Key

  Returns:
    Key
  """

  if isinstance(arg, Key):
    key = arg
  elif isinstance(arg, basestring):

    key = Key(arg)
  elif isinstance(arg, Entity):
    key = arg.key()
  elif not isinstance(arg, Key):
    raise datastore_errors.BadArgumentError(
      'Expects argument to be an Entity or Key; received %s (a %s).' %
      (arg, typename(arg)))
  assert isinstance(key, Key)


  if not key.has_id_or_name():
    raise datastore_errors.BadKeyError('Key %r is not complete.' % key)

  return key


def _GetPropertyValue(entity, property):
  """Returns an entity's value for a given property name.

  Handles special properties like __key__ as well as normal properties.

  Args:
    entity: datastore.Entity
    property: str; the property name

  Returns:
    property value. For __key__, a datastore_types.Key.

  Raises:
    KeyError, if the entity does not have the given property.
  """
  if property in datastore_types._SPECIAL_PROPERTIES:
    if property == datastore_types._UNAPPLIED_LOG_TIMESTAMP_SPECIAL_PROPERTY:
      raise KeyError(property)

    assert property == datastore_types._KEY_SPECIAL_PROPERTY
    return entity.key()
  else:
    return entity[property]


def _AddOrAppend(dictionary, key, value):
  """Adds the value to the existing values in the dictionary, if any.

  If dictionary[key] doesn't exist, sets dictionary[key] to value.

  If dictionary[key] is not a list, sets dictionary[key] to [old_value, value].

  If dictionary[key] is a list, appends value to that list.

  Args:
    dictionary: a dict
    key, value: anything
  """
  if key in dictionary:
    existing_value = dictionary[key]
    if isinstance(existing_value, list):
      existing_value.append(value)
    else:
      dictionary[key] = [existing_value, value]
  else:
    dictionary[key] = value


class Iterator(datastore_query.ResultsIterator):
  """Thin wrapper of datastore_query.ResultsIterator.

  Deprecated, do not use, only for backwards compatability.
  """
  def _Next(self, count=None):
    if count is None:
      count = 20
    result = []
    for r in self:
      if len(result) >= count:
        break;
      result.append(r)
    return result

  def GetCompiledCursor(self, query):
    return self.cursor()

  _Get = _Next



DatastoreRPC = apiproxy_stub_map.UserRPC
GetRpcFromKwargs = _GetConfigFromKwargs
_CurrentTransactionKey = IsInTransaction
_ToDatastoreError = datastore_rpc._ToDatastoreError
_DatastoreExceptionFromErrorCodeAndDetail = datastore_rpc._DatastoreExceptionFromErrorCodeAndDetail
