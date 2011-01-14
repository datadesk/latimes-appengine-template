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

from google.net.proto import ProtocolBuffer
import array
import dummy_thread as thread

__pychecker__ = """maxreturns=0 maxbranches=0 no-callinit
                   unusednames=printElemNumber,debug_strs no-special"""

from google.appengine.api.api_base_pb import *
import google.appengine.api.api_base_pb
class ChannelServiceError(ProtocolBuffer.ProtocolMessage):

  OK           =    0
  INTERNAL_ERROR =    1
  INVALID_CHANNEL_KEY =    2
  BAD_MESSAGE  =    3

  _ErrorCode_NAMES = {
    0: "OK",
    1: "INTERNAL_ERROR",
    2: "INVALID_CHANNEL_KEY",
    3: "BAD_MESSAGE",
  }

  def ErrorCode_Name(cls, x): return cls._ErrorCode_NAMES.get(x, "")
  ErrorCode_Name = classmethod(ErrorCode_Name)


  def __init__(self, contents=None):
    pass
    if contents is not None: self.MergeFromString(contents)


  def MergeFrom(self, x):
    assert x is not self

  def Equals(self, x):
    if x is self: return 1
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    return n + 0

  def Clear(self):
    pass

  def OutputUnchecked(self, out):
    pass

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])


  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
  }, 0)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
  }, 0, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class CreateChannelRequest(ProtocolBuffer.ProtocolMessage):
  has_application_key_ = 0
  application_key_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def application_key(self): return self.application_key_

  def set_application_key(self, x):
    self.has_application_key_ = 1
    self.application_key_ = x

  def clear_application_key(self):
    if self.has_application_key_:
      self.has_application_key_ = 0
      self.application_key_ = ""

  def has_application_key(self): return self.has_application_key_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_application_key()): self.set_application_key(x.application_key())

  def Equals(self, x):
    if x is self: return 1
    if self.has_application_key_ != x.has_application_key_: return 0
    if self.has_application_key_ and self.application_key_ != x.application_key_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_application_key_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: application_key not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.application_key_))
    return n + 1

  def Clear(self):
    self.clear_application_key()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.application_key_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_application_key(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_application_key_: res+=prefix+("application_key: %s\n" % self.DebugFormatString(self.application_key_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kapplication_key = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "application_key",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class CreateChannelResponse(ProtocolBuffer.ProtocolMessage):
  has_client_id_ = 0
  client_id_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def client_id(self): return self.client_id_

  def set_client_id(self, x):
    self.has_client_id_ = 1
    self.client_id_ = x

  def clear_client_id(self):
    if self.has_client_id_:
      self.has_client_id_ = 0
      self.client_id_ = ""

  def has_client_id(self): return self.has_client_id_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_client_id()): self.set_client_id(x.client_id())

  def Equals(self, x):
    if x is self: return 1
    if self.has_client_id_ != x.has_client_id_: return 0
    if self.has_client_id_ and self.client_id_ != x.client_id_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    if (self.has_client_id_): n += 1 + self.lengthString(len(self.client_id_))
    return n + 0

  def Clear(self):
    self.clear_client_id()

  def OutputUnchecked(self, out):
    if (self.has_client_id_):
      out.putVarInt32(18)
      out.putPrefixedString(self.client_id_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 18:
        self.set_client_id(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_client_id_: res+=prefix+("client_id: %s\n" % self.DebugFormatString(self.client_id_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kclient_id = 2

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    2: "client_id",
  }, 2)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    2: ProtocolBuffer.Encoder.STRING,
  }, 2, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class SendMessageRequest(ProtocolBuffer.ProtocolMessage):
  has_application_key_ = 0
  application_key_ = ""
  has_message_ = 0
  message_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def application_key(self): return self.application_key_

  def set_application_key(self, x):
    self.has_application_key_ = 1
    self.application_key_ = x

  def clear_application_key(self):
    if self.has_application_key_:
      self.has_application_key_ = 0
      self.application_key_ = ""

  def has_application_key(self): return self.has_application_key_

  def message(self): return self.message_

  def set_message(self, x):
    self.has_message_ = 1
    self.message_ = x

  def clear_message(self):
    if self.has_message_:
      self.has_message_ = 0
      self.message_ = ""

  def has_message(self): return self.has_message_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_application_key()): self.set_application_key(x.application_key())
    if (x.has_message()): self.set_message(x.message())

  def Equals(self, x):
    if x is self: return 1
    if self.has_application_key_ != x.has_application_key_: return 0
    if self.has_application_key_ and self.application_key_ != x.application_key_: return 0
    if self.has_message_ != x.has_message_: return 0
    if self.has_message_ and self.message_ != x.message_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_application_key_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: application_key not set.')
    if (not self.has_message_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: message not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.application_key_))
    n += self.lengthString(len(self.message_))
    return n + 2

  def Clear(self):
    self.clear_application_key()
    self.clear_message()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.application_key_)
    out.putVarInt32(18)
    out.putPrefixedString(self.message_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_application_key(d.getPrefixedString())
        continue
      if tt == 18:
        self.set_message(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_application_key_: res+=prefix+("application_key: %s\n" % self.DebugFormatString(self.application_key_))
    if self.has_message_: res+=prefix+("message: %s\n" % self.DebugFormatString(self.message_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kapplication_key = 1
  kmessage = 2

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "application_key",
    2: "message",
  }, 2)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
  }, 2, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""

__all__ = ['ChannelServiceError','CreateChannelRequest','CreateChannelResponse','SendMessageRequest']
