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

class ImagesServiceError(ProtocolBuffer.ProtocolMessage):

  UNSPECIFIED_ERROR =    1
  BAD_TRANSFORM_DATA =    2
  NOT_IMAGE    =    3
  BAD_IMAGE_DATA =    4
  IMAGE_TOO_LARGE =    5
  INVALID_BLOB_KEY =    6

  _ErrorCode_NAMES = {
    1: "UNSPECIFIED_ERROR",
    2: "BAD_TRANSFORM_DATA",
    3: "NOT_IMAGE",
    4: "BAD_IMAGE_DATA",
    5: "IMAGE_TOO_LARGE",
    6: "INVALID_BLOB_KEY",
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
class ImagesServiceTransform(ProtocolBuffer.ProtocolMessage):

  RESIZE       =    1
  ROTATE       =    2
  HORIZONTAL_FLIP =    3
  VERTICAL_FLIP =    4
  CROP         =    5
  IM_FEELING_LUCKY =    6

  _Type_NAMES = {
    1: "RESIZE",
    2: "ROTATE",
    3: "HORIZONTAL_FLIP",
    4: "VERTICAL_FLIP",
    5: "CROP",
    6: "IM_FEELING_LUCKY",
  }

  def Type_Name(cls, x): return cls._Type_NAMES.get(x, "")
  Type_Name = classmethod(Type_Name)


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
class Transform(ProtocolBuffer.ProtocolMessage):
  has_width_ = 0
  width_ = 0
  has_height_ = 0
  height_ = 0
  has_rotate_ = 0
  rotate_ = 0
  has_horizontal_flip_ = 0
  horizontal_flip_ = 0
  has_vertical_flip_ = 0
  vertical_flip_ = 0
  has_crop_left_x_ = 0
  crop_left_x_ = 0.0
  has_crop_top_y_ = 0
  crop_top_y_ = 0.0
  has_crop_right_x_ = 0
  crop_right_x_ = 1.0
  has_crop_bottom_y_ = 0
  crop_bottom_y_ = 1.0
  has_autolevels_ = 0
  autolevels_ = 0

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def width(self): return self.width_

  def set_width(self, x):
    self.has_width_ = 1
    self.width_ = x

  def clear_width(self):
    if self.has_width_:
      self.has_width_ = 0
      self.width_ = 0

  def has_width(self): return self.has_width_

  def height(self): return self.height_

  def set_height(self, x):
    self.has_height_ = 1
    self.height_ = x

  def clear_height(self):
    if self.has_height_:
      self.has_height_ = 0
      self.height_ = 0

  def has_height(self): return self.has_height_

  def rotate(self): return self.rotate_

  def set_rotate(self, x):
    self.has_rotate_ = 1
    self.rotate_ = x

  def clear_rotate(self):
    if self.has_rotate_:
      self.has_rotate_ = 0
      self.rotate_ = 0

  def has_rotate(self): return self.has_rotate_

  def horizontal_flip(self): return self.horizontal_flip_

  def set_horizontal_flip(self, x):
    self.has_horizontal_flip_ = 1
    self.horizontal_flip_ = x

  def clear_horizontal_flip(self):
    if self.has_horizontal_flip_:
      self.has_horizontal_flip_ = 0
      self.horizontal_flip_ = 0

  def has_horizontal_flip(self): return self.has_horizontal_flip_

  def vertical_flip(self): return self.vertical_flip_

  def set_vertical_flip(self, x):
    self.has_vertical_flip_ = 1
    self.vertical_flip_ = x

  def clear_vertical_flip(self):
    if self.has_vertical_flip_:
      self.has_vertical_flip_ = 0
      self.vertical_flip_ = 0

  def has_vertical_flip(self): return self.has_vertical_flip_

  def crop_left_x(self): return self.crop_left_x_

  def set_crop_left_x(self, x):
    self.has_crop_left_x_ = 1
    self.crop_left_x_ = x

  def clear_crop_left_x(self):
    if self.has_crop_left_x_:
      self.has_crop_left_x_ = 0
      self.crop_left_x_ = 0.0

  def has_crop_left_x(self): return self.has_crop_left_x_

  def crop_top_y(self): return self.crop_top_y_

  def set_crop_top_y(self, x):
    self.has_crop_top_y_ = 1
    self.crop_top_y_ = x

  def clear_crop_top_y(self):
    if self.has_crop_top_y_:
      self.has_crop_top_y_ = 0
      self.crop_top_y_ = 0.0

  def has_crop_top_y(self): return self.has_crop_top_y_

  def crop_right_x(self): return self.crop_right_x_

  def set_crop_right_x(self, x):
    self.has_crop_right_x_ = 1
    self.crop_right_x_ = x

  def clear_crop_right_x(self):
    if self.has_crop_right_x_:
      self.has_crop_right_x_ = 0
      self.crop_right_x_ = 1.0

  def has_crop_right_x(self): return self.has_crop_right_x_

  def crop_bottom_y(self): return self.crop_bottom_y_

  def set_crop_bottom_y(self, x):
    self.has_crop_bottom_y_ = 1
    self.crop_bottom_y_ = x

  def clear_crop_bottom_y(self):
    if self.has_crop_bottom_y_:
      self.has_crop_bottom_y_ = 0
      self.crop_bottom_y_ = 1.0

  def has_crop_bottom_y(self): return self.has_crop_bottom_y_

  def autolevels(self): return self.autolevels_

  def set_autolevels(self, x):
    self.has_autolevels_ = 1
    self.autolevels_ = x

  def clear_autolevels(self):
    if self.has_autolevels_:
      self.has_autolevels_ = 0
      self.autolevels_ = 0

  def has_autolevels(self): return self.has_autolevels_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_width()): self.set_width(x.width())
    if (x.has_height()): self.set_height(x.height())
    if (x.has_rotate()): self.set_rotate(x.rotate())
    if (x.has_horizontal_flip()): self.set_horizontal_flip(x.horizontal_flip())
    if (x.has_vertical_flip()): self.set_vertical_flip(x.vertical_flip())
    if (x.has_crop_left_x()): self.set_crop_left_x(x.crop_left_x())
    if (x.has_crop_top_y()): self.set_crop_top_y(x.crop_top_y())
    if (x.has_crop_right_x()): self.set_crop_right_x(x.crop_right_x())
    if (x.has_crop_bottom_y()): self.set_crop_bottom_y(x.crop_bottom_y())
    if (x.has_autolevels()): self.set_autolevels(x.autolevels())

  def Equals(self, x):
    if x is self: return 1
    if self.has_width_ != x.has_width_: return 0
    if self.has_width_ and self.width_ != x.width_: return 0
    if self.has_height_ != x.has_height_: return 0
    if self.has_height_ and self.height_ != x.height_: return 0
    if self.has_rotate_ != x.has_rotate_: return 0
    if self.has_rotate_ and self.rotate_ != x.rotate_: return 0
    if self.has_horizontal_flip_ != x.has_horizontal_flip_: return 0
    if self.has_horizontal_flip_ and self.horizontal_flip_ != x.horizontal_flip_: return 0
    if self.has_vertical_flip_ != x.has_vertical_flip_: return 0
    if self.has_vertical_flip_ and self.vertical_flip_ != x.vertical_flip_: return 0
    if self.has_crop_left_x_ != x.has_crop_left_x_: return 0
    if self.has_crop_left_x_ and self.crop_left_x_ != x.crop_left_x_: return 0
    if self.has_crop_top_y_ != x.has_crop_top_y_: return 0
    if self.has_crop_top_y_ and self.crop_top_y_ != x.crop_top_y_: return 0
    if self.has_crop_right_x_ != x.has_crop_right_x_: return 0
    if self.has_crop_right_x_ and self.crop_right_x_ != x.crop_right_x_: return 0
    if self.has_crop_bottom_y_ != x.has_crop_bottom_y_: return 0
    if self.has_crop_bottom_y_ and self.crop_bottom_y_ != x.crop_bottom_y_: return 0
    if self.has_autolevels_ != x.has_autolevels_: return 0
    if self.has_autolevels_ and self.autolevels_ != x.autolevels_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    if (self.has_width_): n += 1 + self.lengthVarInt64(self.width_)
    if (self.has_height_): n += 1 + self.lengthVarInt64(self.height_)
    if (self.has_rotate_): n += 1 + self.lengthVarInt64(self.rotate_)
    if (self.has_horizontal_flip_): n += 2
    if (self.has_vertical_flip_): n += 2
    if (self.has_crop_left_x_): n += 5
    if (self.has_crop_top_y_): n += 5
    if (self.has_crop_right_x_): n += 5
    if (self.has_crop_bottom_y_): n += 5
    if (self.has_autolevels_): n += 2
    return n + 0

  def Clear(self):
    self.clear_width()
    self.clear_height()
    self.clear_rotate()
    self.clear_horizontal_flip()
    self.clear_vertical_flip()
    self.clear_crop_left_x()
    self.clear_crop_top_y()
    self.clear_crop_right_x()
    self.clear_crop_bottom_y()
    self.clear_autolevels()

  def OutputUnchecked(self, out):
    if (self.has_width_):
      out.putVarInt32(8)
      out.putVarInt32(self.width_)
    if (self.has_height_):
      out.putVarInt32(16)
      out.putVarInt32(self.height_)
    if (self.has_rotate_):
      out.putVarInt32(24)
      out.putVarInt32(self.rotate_)
    if (self.has_horizontal_flip_):
      out.putVarInt32(32)
      out.putBoolean(self.horizontal_flip_)
    if (self.has_vertical_flip_):
      out.putVarInt32(40)
      out.putBoolean(self.vertical_flip_)
    if (self.has_crop_left_x_):
      out.putVarInt32(53)
      out.putFloat(self.crop_left_x_)
    if (self.has_crop_top_y_):
      out.putVarInt32(61)
      out.putFloat(self.crop_top_y_)
    if (self.has_crop_right_x_):
      out.putVarInt32(69)
      out.putFloat(self.crop_right_x_)
    if (self.has_crop_bottom_y_):
      out.putVarInt32(77)
      out.putFloat(self.crop_bottom_y_)
    if (self.has_autolevels_):
      out.putVarInt32(80)
      out.putBoolean(self.autolevels_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 8:
        self.set_width(d.getVarInt32())
        continue
      if tt == 16:
        self.set_height(d.getVarInt32())
        continue
      if tt == 24:
        self.set_rotate(d.getVarInt32())
        continue
      if tt == 32:
        self.set_horizontal_flip(d.getBoolean())
        continue
      if tt == 40:
        self.set_vertical_flip(d.getBoolean())
        continue
      if tt == 53:
        self.set_crop_left_x(d.getFloat())
        continue
      if tt == 61:
        self.set_crop_top_y(d.getFloat())
        continue
      if tt == 69:
        self.set_crop_right_x(d.getFloat())
        continue
      if tt == 77:
        self.set_crop_bottom_y(d.getFloat())
        continue
      if tt == 80:
        self.set_autolevels(d.getBoolean())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_width_: res+=prefix+("width: %s\n" % self.DebugFormatInt32(self.width_))
    if self.has_height_: res+=prefix+("height: %s\n" % self.DebugFormatInt32(self.height_))
    if self.has_rotate_: res+=prefix+("rotate: %s\n" % self.DebugFormatInt32(self.rotate_))
    if self.has_horizontal_flip_: res+=prefix+("horizontal_flip: %s\n" % self.DebugFormatBool(self.horizontal_flip_))
    if self.has_vertical_flip_: res+=prefix+("vertical_flip: %s\n" % self.DebugFormatBool(self.vertical_flip_))
    if self.has_crop_left_x_: res+=prefix+("crop_left_x: %s\n" % self.DebugFormatFloat(self.crop_left_x_))
    if self.has_crop_top_y_: res+=prefix+("crop_top_y: %s\n" % self.DebugFormatFloat(self.crop_top_y_))
    if self.has_crop_right_x_: res+=prefix+("crop_right_x: %s\n" % self.DebugFormatFloat(self.crop_right_x_))
    if self.has_crop_bottom_y_: res+=prefix+("crop_bottom_y: %s\n" % self.DebugFormatFloat(self.crop_bottom_y_))
    if self.has_autolevels_: res+=prefix+("autolevels: %s\n" % self.DebugFormatBool(self.autolevels_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kwidth = 1
  kheight = 2
  krotate = 3
  khorizontal_flip = 4
  kvertical_flip = 5
  kcrop_left_x = 6
  kcrop_top_y = 7
  kcrop_right_x = 8
  kcrop_bottom_y = 9
  kautolevels = 10

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "width",
    2: "height",
    3: "rotate",
    4: "horizontal_flip",
    5: "vertical_flip",
    6: "crop_left_x",
    7: "crop_top_y",
    8: "crop_right_x",
    9: "crop_bottom_y",
    10: "autolevels",
  }, 10)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.NUMERIC,
    2: ProtocolBuffer.Encoder.NUMERIC,
    3: ProtocolBuffer.Encoder.NUMERIC,
    4: ProtocolBuffer.Encoder.NUMERIC,
    5: ProtocolBuffer.Encoder.NUMERIC,
    6: ProtocolBuffer.Encoder.FLOAT,
    7: ProtocolBuffer.Encoder.FLOAT,
    8: ProtocolBuffer.Encoder.FLOAT,
    9: ProtocolBuffer.Encoder.FLOAT,
    10: ProtocolBuffer.Encoder.NUMERIC,
  }, 10, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class ImageData(ProtocolBuffer.ProtocolMessage):
  has_content_ = 0
  content_ = ""
  has_blob_key_ = 0
  blob_key_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def content(self): return self.content_

  def set_content(self, x):
    self.has_content_ = 1
    self.content_ = x

  def clear_content(self):
    if self.has_content_:
      self.has_content_ = 0
      self.content_ = ""

  def has_content(self): return self.has_content_

  def blob_key(self): return self.blob_key_

  def set_blob_key(self, x):
    self.has_blob_key_ = 1
    self.blob_key_ = x

  def clear_blob_key(self):
    if self.has_blob_key_:
      self.has_blob_key_ = 0
      self.blob_key_ = ""

  def has_blob_key(self): return self.has_blob_key_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_content()): self.set_content(x.content())
    if (x.has_blob_key()): self.set_blob_key(x.blob_key())

  def Equals(self, x):
    if x is self: return 1
    if self.has_content_ != x.has_content_: return 0
    if self.has_content_ and self.content_ != x.content_: return 0
    if self.has_blob_key_ != x.has_blob_key_: return 0
    if self.has_blob_key_ and self.blob_key_ != x.blob_key_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_content_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: content not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.content_))
    if (self.has_blob_key_): n += 1 + self.lengthString(len(self.blob_key_))
    return n + 1

  def Clear(self):
    self.clear_content()
    self.clear_blob_key()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.content_)
    if (self.has_blob_key_):
      out.putVarInt32(18)
      out.putPrefixedString(self.blob_key_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_content(d.getPrefixedString())
        continue
      if tt == 18:
        self.set_blob_key(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_content_: res+=prefix+("content: %s\n" % self.DebugFormatString(self.content_))
    if self.has_blob_key_: res+=prefix+("blob_key: %s\n" % self.DebugFormatString(self.blob_key_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kcontent = 1
  kblob_key = 2

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "content",
    2: "blob_key",
  }, 2)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
  }, 2, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class OutputSettings(ProtocolBuffer.ProtocolMessage):

  PNG          =    0
  JPEG         =    1

  _MIME_TYPE_NAMES = {
    0: "PNG",
    1: "JPEG",
  }

  def MIME_TYPE_Name(cls, x): return cls._MIME_TYPE_NAMES.get(x, "")
  MIME_TYPE_Name = classmethod(MIME_TYPE_Name)

  has_mime_type_ = 0
  mime_type_ = 0

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def mime_type(self): return self.mime_type_

  def set_mime_type(self, x):
    self.has_mime_type_ = 1
    self.mime_type_ = x

  def clear_mime_type(self):
    if self.has_mime_type_:
      self.has_mime_type_ = 0
      self.mime_type_ = 0

  def has_mime_type(self): return self.has_mime_type_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_mime_type()): self.set_mime_type(x.mime_type())

  def Equals(self, x):
    if x is self: return 1
    if self.has_mime_type_ != x.has_mime_type_: return 0
    if self.has_mime_type_ and self.mime_type_ != x.mime_type_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    if (self.has_mime_type_): n += 1 + self.lengthVarInt64(self.mime_type_)
    return n + 0

  def Clear(self):
    self.clear_mime_type()

  def OutputUnchecked(self, out):
    if (self.has_mime_type_):
      out.putVarInt32(8)
      out.putVarInt32(self.mime_type_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 8:
        self.set_mime_type(d.getVarInt32())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_mime_type_: res+=prefix+("mime_type: %s\n" % self.DebugFormatInt32(self.mime_type_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kmime_type = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "mime_type",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.NUMERIC,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class ImagesTransformRequest(ProtocolBuffer.ProtocolMessage):
  has_image_ = 0
  has_output_ = 0

  def __init__(self, contents=None):
    self.image_ = ImageData()
    self.transform_ = []
    self.output_ = OutputSettings()
    if contents is not None: self.MergeFromString(contents)

  def image(self): return self.image_

  def mutable_image(self): self.has_image_ = 1; return self.image_

  def clear_image(self):self.has_image_ = 0; self.image_.Clear()

  def has_image(self): return self.has_image_

  def transform_size(self): return len(self.transform_)
  def transform_list(self): return self.transform_

  def transform(self, i):
    return self.transform_[i]

  def mutable_transform(self, i):
    return self.transform_[i]

  def add_transform(self):
    x = Transform()
    self.transform_.append(x)
    return x

  def clear_transform(self):
    self.transform_ = []
  def output(self): return self.output_

  def mutable_output(self): self.has_output_ = 1; return self.output_

  def clear_output(self):self.has_output_ = 0; self.output_.Clear()

  def has_output(self): return self.has_output_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_image()): self.mutable_image().MergeFrom(x.image())
    for i in xrange(x.transform_size()): self.add_transform().CopyFrom(x.transform(i))
    if (x.has_output()): self.mutable_output().MergeFrom(x.output())

  def Equals(self, x):
    if x is self: return 1
    if self.has_image_ != x.has_image_: return 0
    if self.has_image_ and self.image_ != x.image_: return 0
    if len(self.transform_) != len(x.transform_): return 0
    for e1, e2 in zip(self.transform_, x.transform_):
      if e1 != e2: return 0
    if self.has_output_ != x.has_output_: return 0
    if self.has_output_ and self.output_ != x.output_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_image_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: image not set.')
    elif not self.image_.IsInitialized(debug_strs): initialized = 0
    for p in self.transform_:
      if not p.IsInitialized(debug_strs): initialized=0
    if (not self.has_output_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: output not set.')
    elif not self.output_.IsInitialized(debug_strs): initialized = 0
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(self.image_.ByteSize())
    n += 1 * len(self.transform_)
    for i in xrange(len(self.transform_)): n += self.lengthString(self.transform_[i].ByteSize())
    n += self.lengthString(self.output_.ByteSize())
    return n + 2

  def Clear(self):
    self.clear_image()
    self.clear_transform()
    self.clear_output()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putVarInt32(self.image_.ByteSize())
    self.image_.OutputUnchecked(out)
    for i in xrange(len(self.transform_)):
      out.putVarInt32(18)
      out.putVarInt32(self.transform_[i].ByteSize())
      self.transform_[i].OutputUnchecked(out)
    out.putVarInt32(26)
    out.putVarInt32(self.output_.ByteSize())
    self.output_.OutputUnchecked(out)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.mutable_image().TryMerge(tmp)
        continue
      if tt == 18:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.add_transform().TryMerge(tmp)
        continue
      if tt == 26:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.mutable_output().TryMerge(tmp)
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_image_:
      res+=prefix+"image <\n"
      res+=self.image_.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
    cnt=0
    for e in self.transform_:
      elm=""
      if printElemNumber: elm="(%d)" % cnt
      res+=prefix+("transform%s <\n" % elm)
      res+=e.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
      cnt+=1
    if self.has_output_:
      res+=prefix+"output <\n"
      res+=self.output_.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kimage = 1
  ktransform = 2
  koutput = 3

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "image",
    2: "transform",
    3: "output",
  }, 3)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
    3: ProtocolBuffer.Encoder.STRING,
  }, 3, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class ImagesTransformResponse(ProtocolBuffer.ProtocolMessage):
  has_image_ = 0

  def __init__(self, contents=None):
    self.image_ = ImageData()
    if contents is not None: self.MergeFromString(contents)

  def image(self): return self.image_

  def mutable_image(self): self.has_image_ = 1; return self.image_

  def clear_image(self):self.has_image_ = 0; self.image_.Clear()

  def has_image(self): return self.has_image_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_image()): self.mutable_image().MergeFrom(x.image())

  def Equals(self, x):
    if x is self: return 1
    if self.has_image_ != x.has_image_: return 0
    if self.has_image_ and self.image_ != x.image_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_image_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: image not set.')
    elif not self.image_.IsInitialized(debug_strs): initialized = 0
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(self.image_.ByteSize())
    return n + 1

  def Clear(self):
    self.clear_image()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putVarInt32(self.image_.ByteSize())
    self.image_.OutputUnchecked(out)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.mutable_image().TryMerge(tmp)
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_image_:
      res+=prefix+"image <\n"
      res+=self.image_.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kimage = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "image",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class CompositeImageOptions(ProtocolBuffer.ProtocolMessage):

  TOP_LEFT     =    0
  TOP          =    1
  TOP_RIGHT    =    2
  LEFT         =    3
  CENTER       =    4
  RIGHT        =    5
  BOTTOM_LEFT  =    6
  BOTTOM       =    7
  BOTTOM_RIGHT =    8

  _ANCHOR_NAMES = {
    0: "TOP_LEFT",
    1: "TOP",
    2: "TOP_RIGHT",
    3: "LEFT",
    4: "CENTER",
    5: "RIGHT",
    6: "BOTTOM_LEFT",
    7: "BOTTOM",
    8: "BOTTOM_RIGHT",
  }

  def ANCHOR_Name(cls, x): return cls._ANCHOR_NAMES.get(x, "")
  ANCHOR_Name = classmethod(ANCHOR_Name)

  has_source_index_ = 0
  source_index_ = 0
  has_x_offset_ = 0
  x_offset_ = 0
  has_y_offset_ = 0
  y_offset_ = 0
  has_opacity_ = 0
  opacity_ = 0.0
  has_anchor_ = 0
  anchor_ = 0

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def source_index(self): return self.source_index_

  def set_source_index(self, x):
    self.has_source_index_ = 1
    self.source_index_ = x

  def clear_source_index(self):
    if self.has_source_index_:
      self.has_source_index_ = 0
      self.source_index_ = 0

  def has_source_index(self): return self.has_source_index_

  def x_offset(self): return self.x_offset_

  def set_x_offset(self, x):
    self.has_x_offset_ = 1
    self.x_offset_ = x

  def clear_x_offset(self):
    if self.has_x_offset_:
      self.has_x_offset_ = 0
      self.x_offset_ = 0

  def has_x_offset(self): return self.has_x_offset_

  def y_offset(self): return self.y_offset_

  def set_y_offset(self, x):
    self.has_y_offset_ = 1
    self.y_offset_ = x

  def clear_y_offset(self):
    if self.has_y_offset_:
      self.has_y_offset_ = 0
      self.y_offset_ = 0

  def has_y_offset(self): return self.has_y_offset_

  def opacity(self): return self.opacity_

  def set_opacity(self, x):
    self.has_opacity_ = 1
    self.opacity_ = x

  def clear_opacity(self):
    if self.has_opacity_:
      self.has_opacity_ = 0
      self.opacity_ = 0.0

  def has_opacity(self): return self.has_opacity_

  def anchor(self): return self.anchor_

  def set_anchor(self, x):
    self.has_anchor_ = 1
    self.anchor_ = x

  def clear_anchor(self):
    if self.has_anchor_:
      self.has_anchor_ = 0
      self.anchor_ = 0

  def has_anchor(self): return self.has_anchor_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_source_index()): self.set_source_index(x.source_index())
    if (x.has_x_offset()): self.set_x_offset(x.x_offset())
    if (x.has_y_offset()): self.set_y_offset(x.y_offset())
    if (x.has_opacity()): self.set_opacity(x.opacity())
    if (x.has_anchor()): self.set_anchor(x.anchor())

  def Equals(self, x):
    if x is self: return 1
    if self.has_source_index_ != x.has_source_index_: return 0
    if self.has_source_index_ and self.source_index_ != x.source_index_: return 0
    if self.has_x_offset_ != x.has_x_offset_: return 0
    if self.has_x_offset_ and self.x_offset_ != x.x_offset_: return 0
    if self.has_y_offset_ != x.has_y_offset_: return 0
    if self.has_y_offset_ and self.y_offset_ != x.y_offset_: return 0
    if self.has_opacity_ != x.has_opacity_: return 0
    if self.has_opacity_ and self.opacity_ != x.opacity_: return 0
    if self.has_anchor_ != x.has_anchor_: return 0
    if self.has_anchor_ and self.anchor_ != x.anchor_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_source_index_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: source_index not set.')
    if (not self.has_x_offset_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: x_offset not set.')
    if (not self.has_y_offset_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: y_offset not set.')
    if (not self.has_opacity_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: opacity not set.')
    if (not self.has_anchor_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: anchor not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthVarInt64(self.source_index_)
    n += self.lengthVarInt64(self.x_offset_)
    n += self.lengthVarInt64(self.y_offset_)
    n += self.lengthVarInt64(self.anchor_)
    return n + 9

  def Clear(self):
    self.clear_source_index()
    self.clear_x_offset()
    self.clear_y_offset()
    self.clear_opacity()
    self.clear_anchor()

  def OutputUnchecked(self, out):
    out.putVarInt32(8)
    out.putVarInt32(self.source_index_)
    out.putVarInt32(16)
    out.putVarInt32(self.x_offset_)
    out.putVarInt32(24)
    out.putVarInt32(self.y_offset_)
    out.putVarInt32(37)
    out.putFloat(self.opacity_)
    out.putVarInt32(40)
    out.putVarInt32(self.anchor_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 8:
        self.set_source_index(d.getVarInt32())
        continue
      if tt == 16:
        self.set_x_offset(d.getVarInt32())
        continue
      if tt == 24:
        self.set_y_offset(d.getVarInt32())
        continue
      if tt == 37:
        self.set_opacity(d.getFloat())
        continue
      if tt == 40:
        self.set_anchor(d.getVarInt32())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_source_index_: res+=prefix+("source_index: %s\n" % self.DebugFormatInt32(self.source_index_))
    if self.has_x_offset_: res+=prefix+("x_offset: %s\n" % self.DebugFormatInt32(self.x_offset_))
    if self.has_y_offset_: res+=prefix+("y_offset: %s\n" % self.DebugFormatInt32(self.y_offset_))
    if self.has_opacity_: res+=prefix+("opacity: %s\n" % self.DebugFormatFloat(self.opacity_))
    if self.has_anchor_: res+=prefix+("anchor: %s\n" % self.DebugFormatInt32(self.anchor_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  ksource_index = 1
  kx_offset = 2
  ky_offset = 3
  kopacity = 4
  kanchor = 5

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "source_index",
    2: "x_offset",
    3: "y_offset",
    4: "opacity",
    5: "anchor",
  }, 5)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.NUMERIC,
    2: ProtocolBuffer.Encoder.NUMERIC,
    3: ProtocolBuffer.Encoder.NUMERIC,
    4: ProtocolBuffer.Encoder.FLOAT,
    5: ProtocolBuffer.Encoder.NUMERIC,
  }, 5, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class ImagesCanvas(ProtocolBuffer.ProtocolMessage):
  has_width_ = 0
  width_ = 0
  has_height_ = 0
  height_ = 0
  has_output_ = 0
  has_color_ = 0
  color_ = -1

  def __init__(self, contents=None):
    self.output_ = OutputSettings()
    if contents is not None: self.MergeFromString(contents)

  def width(self): return self.width_

  def set_width(self, x):
    self.has_width_ = 1
    self.width_ = x

  def clear_width(self):
    if self.has_width_:
      self.has_width_ = 0
      self.width_ = 0

  def has_width(self): return self.has_width_

  def height(self): return self.height_

  def set_height(self, x):
    self.has_height_ = 1
    self.height_ = x

  def clear_height(self):
    if self.has_height_:
      self.has_height_ = 0
      self.height_ = 0

  def has_height(self): return self.has_height_

  def output(self): return self.output_

  def mutable_output(self): self.has_output_ = 1; return self.output_

  def clear_output(self):self.has_output_ = 0; self.output_.Clear()

  def has_output(self): return self.has_output_

  def color(self): return self.color_

  def set_color(self, x):
    self.has_color_ = 1
    self.color_ = x

  def clear_color(self):
    if self.has_color_:
      self.has_color_ = 0
      self.color_ = -1

  def has_color(self): return self.has_color_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_width()): self.set_width(x.width())
    if (x.has_height()): self.set_height(x.height())
    if (x.has_output()): self.mutable_output().MergeFrom(x.output())
    if (x.has_color()): self.set_color(x.color())

  def Equals(self, x):
    if x is self: return 1
    if self.has_width_ != x.has_width_: return 0
    if self.has_width_ and self.width_ != x.width_: return 0
    if self.has_height_ != x.has_height_: return 0
    if self.has_height_ and self.height_ != x.height_: return 0
    if self.has_output_ != x.has_output_: return 0
    if self.has_output_ and self.output_ != x.output_: return 0
    if self.has_color_ != x.has_color_: return 0
    if self.has_color_ and self.color_ != x.color_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_width_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: width not set.')
    if (not self.has_height_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: height not set.')
    if (not self.has_output_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: output not set.')
    elif not self.output_.IsInitialized(debug_strs): initialized = 0
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthVarInt64(self.width_)
    n += self.lengthVarInt64(self.height_)
    n += self.lengthString(self.output_.ByteSize())
    if (self.has_color_): n += 1 + self.lengthVarInt64(self.color_)
    return n + 3

  def Clear(self):
    self.clear_width()
    self.clear_height()
    self.clear_output()
    self.clear_color()

  def OutputUnchecked(self, out):
    out.putVarInt32(8)
    out.putVarInt32(self.width_)
    out.putVarInt32(16)
    out.putVarInt32(self.height_)
    out.putVarInt32(26)
    out.putVarInt32(self.output_.ByteSize())
    self.output_.OutputUnchecked(out)
    if (self.has_color_):
      out.putVarInt32(32)
      out.putVarInt32(self.color_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 8:
        self.set_width(d.getVarInt32())
        continue
      if tt == 16:
        self.set_height(d.getVarInt32())
        continue
      if tt == 26:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.mutable_output().TryMerge(tmp)
        continue
      if tt == 32:
        self.set_color(d.getVarInt32())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_width_: res+=prefix+("width: %s\n" % self.DebugFormatInt32(self.width_))
    if self.has_height_: res+=prefix+("height: %s\n" % self.DebugFormatInt32(self.height_))
    if self.has_output_:
      res+=prefix+"output <\n"
      res+=self.output_.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
    if self.has_color_: res+=prefix+("color: %s\n" % self.DebugFormatInt32(self.color_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kwidth = 1
  kheight = 2
  koutput = 3
  kcolor = 4

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "width",
    2: "height",
    3: "output",
    4: "color",
  }, 4)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.NUMERIC,
    2: ProtocolBuffer.Encoder.NUMERIC,
    3: ProtocolBuffer.Encoder.STRING,
    4: ProtocolBuffer.Encoder.NUMERIC,
  }, 4, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class ImagesCompositeRequest(ProtocolBuffer.ProtocolMessage):
  has_canvas_ = 0

  def __init__(self, contents=None):
    self.image_ = []
    self.options_ = []
    self.canvas_ = ImagesCanvas()
    if contents is not None: self.MergeFromString(contents)

  def image_size(self): return len(self.image_)
  def image_list(self): return self.image_

  def image(self, i):
    return self.image_[i]

  def mutable_image(self, i):
    return self.image_[i]

  def add_image(self):
    x = ImageData()
    self.image_.append(x)
    return x

  def clear_image(self):
    self.image_ = []
  def options_size(self): return len(self.options_)
  def options_list(self): return self.options_

  def options(self, i):
    return self.options_[i]

  def mutable_options(self, i):
    return self.options_[i]

  def add_options(self):
    x = CompositeImageOptions()
    self.options_.append(x)
    return x

  def clear_options(self):
    self.options_ = []
  def canvas(self): return self.canvas_

  def mutable_canvas(self): self.has_canvas_ = 1; return self.canvas_

  def clear_canvas(self):self.has_canvas_ = 0; self.canvas_.Clear()

  def has_canvas(self): return self.has_canvas_


  def MergeFrom(self, x):
    assert x is not self
    for i in xrange(x.image_size()): self.add_image().CopyFrom(x.image(i))
    for i in xrange(x.options_size()): self.add_options().CopyFrom(x.options(i))
    if (x.has_canvas()): self.mutable_canvas().MergeFrom(x.canvas())

  def Equals(self, x):
    if x is self: return 1
    if len(self.image_) != len(x.image_): return 0
    for e1, e2 in zip(self.image_, x.image_):
      if e1 != e2: return 0
    if len(self.options_) != len(x.options_): return 0
    for e1, e2 in zip(self.options_, x.options_):
      if e1 != e2: return 0
    if self.has_canvas_ != x.has_canvas_: return 0
    if self.has_canvas_ and self.canvas_ != x.canvas_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    for p in self.image_:
      if not p.IsInitialized(debug_strs): initialized=0
    for p in self.options_:
      if not p.IsInitialized(debug_strs): initialized=0
    if (not self.has_canvas_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: canvas not set.')
    elif not self.canvas_.IsInitialized(debug_strs): initialized = 0
    return initialized

  def ByteSize(self):
    n = 0
    n += 1 * len(self.image_)
    for i in xrange(len(self.image_)): n += self.lengthString(self.image_[i].ByteSize())
    n += 1 * len(self.options_)
    for i in xrange(len(self.options_)): n += self.lengthString(self.options_[i].ByteSize())
    n += self.lengthString(self.canvas_.ByteSize())
    return n + 1

  def Clear(self):
    self.clear_image()
    self.clear_options()
    self.clear_canvas()

  def OutputUnchecked(self, out):
    for i in xrange(len(self.image_)):
      out.putVarInt32(10)
      out.putVarInt32(self.image_[i].ByteSize())
      self.image_[i].OutputUnchecked(out)
    for i in xrange(len(self.options_)):
      out.putVarInt32(18)
      out.putVarInt32(self.options_[i].ByteSize())
      self.options_[i].OutputUnchecked(out)
    out.putVarInt32(26)
    out.putVarInt32(self.canvas_.ByteSize())
    self.canvas_.OutputUnchecked(out)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.add_image().TryMerge(tmp)
        continue
      if tt == 18:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.add_options().TryMerge(tmp)
        continue
      if tt == 26:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.mutable_canvas().TryMerge(tmp)
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    cnt=0
    for e in self.image_:
      elm=""
      if printElemNumber: elm="(%d)" % cnt
      res+=prefix+("image%s <\n" % elm)
      res+=e.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
      cnt+=1
    cnt=0
    for e in self.options_:
      elm=""
      if printElemNumber: elm="(%d)" % cnt
      res+=prefix+("options%s <\n" % elm)
      res+=e.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
      cnt+=1
    if self.has_canvas_:
      res+=prefix+"canvas <\n"
      res+=self.canvas_.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kimage = 1
  koptions = 2
  kcanvas = 3

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "image",
    2: "options",
    3: "canvas",
  }, 3)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
    3: ProtocolBuffer.Encoder.STRING,
  }, 3, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class ImagesCompositeResponse(ProtocolBuffer.ProtocolMessage):
  has_image_ = 0

  def __init__(self, contents=None):
    self.image_ = ImageData()
    if contents is not None: self.MergeFromString(contents)

  def image(self): return self.image_

  def mutable_image(self): self.has_image_ = 1; return self.image_

  def clear_image(self):self.has_image_ = 0; self.image_.Clear()

  def has_image(self): return self.has_image_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_image()): self.mutable_image().MergeFrom(x.image())

  def Equals(self, x):
    if x is self: return 1
    if self.has_image_ != x.has_image_: return 0
    if self.has_image_ and self.image_ != x.image_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_image_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: image not set.')
    elif not self.image_.IsInitialized(debug_strs): initialized = 0
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(self.image_.ByteSize())
    return n + 1

  def Clear(self):
    self.clear_image()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putVarInt32(self.image_.ByteSize())
    self.image_.OutputUnchecked(out)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.mutable_image().TryMerge(tmp)
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_image_:
      res+=prefix+"image <\n"
      res+=self.image_.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kimage = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "image",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class ImagesHistogramRequest(ProtocolBuffer.ProtocolMessage):
  has_image_ = 0

  def __init__(self, contents=None):
    self.image_ = ImageData()
    if contents is not None: self.MergeFromString(contents)

  def image(self): return self.image_

  def mutable_image(self): self.has_image_ = 1; return self.image_

  def clear_image(self):self.has_image_ = 0; self.image_.Clear()

  def has_image(self): return self.has_image_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_image()): self.mutable_image().MergeFrom(x.image())

  def Equals(self, x):
    if x is self: return 1
    if self.has_image_ != x.has_image_: return 0
    if self.has_image_ and self.image_ != x.image_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_image_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: image not set.')
    elif not self.image_.IsInitialized(debug_strs): initialized = 0
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(self.image_.ByteSize())
    return n + 1

  def Clear(self):
    self.clear_image()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putVarInt32(self.image_.ByteSize())
    self.image_.OutputUnchecked(out)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.mutable_image().TryMerge(tmp)
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_image_:
      res+=prefix+"image <\n"
      res+=self.image_.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kimage = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "image",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class ImagesHistogram(ProtocolBuffer.ProtocolMessage):

  def __init__(self, contents=None):
    self.red_ = []
    self.green_ = []
    self.blue_ = []
    if contents is not None: self.MergeFromString(contents)

  def red_size(self): return len(self.red_)
  def red_list(self): return self.red_

  def red(self, i):
    return self.red_[i]

  def set_red(self, i, x):
    self.red_[i] = x

  def add_red(self, x):
    self.red_.append(x)

  def clear_red(self):
    self.red_ = []

  def green_size(self): return len(self.green_)
  def green_list(self): return self.green_

  def green(self, i):
    return self.green_[i]

  def set_green(self, i, x):
    self.green_[i] = x

  def add_green(self, x):
    self.green_.append(x)

  def clear_green(self):
    self.green_ = []

  def blue_size(self): return len(self.blue_)
  def blue_list(self): return self.blue_

  def blue(self, i):
    return self.blue_[i]

  def set_blue(self, i, x):
    self.blue_[i] = x

  def add_blue(self, x):
    self.blue_.append(x)

  def clear_blue(self):
    self.blue_ = []


  def MergeFrom(self, x):
    assert x is not self
    for i in xrange(x.red_size()): self.add_red(x.red(i))
    for i in xrange(x.green_size()): self.add_green(x.green(i))
    for i in xrange(x.blue_size()): self.add_blue(x.blue(i))

  def Equals(self, x):
    if x is self: return 1
    if len(self.red_) != len(x.red_): return 0
    for e1, e2 in zip(self.red_, x.red_):
      if e1 != e2: return 0
    if len(self.green_) != len(x.green_): return 0
    for e1, e2 in zip(self.green_, x.green_):
      if e1 != e2: return 0
    if len(self.blue_) != len(x.blue_): return 0
    for e1, e2 in zip(self.blue_, x.blue_):
      if e1 != e2: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    n += 1 * len(self.red_)
    for i in xrange(len(self.red_)): n += self.lengthVarInt64(self.red_[i])
    n += 1 * len(self.green_)
    for i in xrange(len(self.green_)): n += self.lengthVarInt64(self.green_[i])
    n += 1 * len(self.blue_)
    for i in xrange(len(self.blue_)): n += self.lengthVarInt64(self.blue_[i])
    return n + 0

  def Clear(self):
    self.clear_red()
    self.clear_green()
    self.clear_blue()

  def OutputUnchecked(self, out):
    for i in xrange(len(self.red_)):
      out.putVarInt32(8)
      out.putVarInt32(self.red_[i])
    for i in xrange(len(self.green_)):
      out.putVarInt32(16)
      out.putVarInt32(self.green_[i])
    for i in xrange(len(self.blue_)):
      out.putVarInt32(24)
      out.putVarInt32(self.blue_[i])

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 8:
        self.add_red(d.getVarInt32())
        continue
      if tt == 16:
        self.add_green(d.getVarInt32())
        continue
      if tt == 24:
        self.add_blue(d.getVarInt32())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    cnt=0
    for e in self.red_:
      elm=""
      if printElemNumber: elm="(%d)" % cnt
      res+=prefix+("red%s: %s\n" % (elm, self.DebugFormatInt32(e)))
      cnt+=1
    cnt=0
    for e in self.green_:
      elm=""
      if printElemNumber: elm="(%d)" % cnt
      res+=prefix+("green%s: %s\n" % (elm, self.DebugFormatInt32(e)))
      cnt+=1
    cnt=0
    for e in self.blue_:
      elm=""
      if printElemNumber: elm="(%d)" % cnt
      res+=prefix+("blue%s: %s\n" % (elm, self.DebugFormatInt32(e)))
      cnt+=1
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kred = 1
  kgreen = 2
  kblue = 3

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "red",
    2: "green",
    3: "blue",
  }, 3)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.NUMERIC,
    2: ProtocolBuffer.Encoder.NUMERIC,
    3: ProtocolBuffer.Encoder.NUMERIC,
  }, 3, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class ImagesHistogramResponse(ProtocolBuffer.ProtocolMessage):
  has_histogram_ = 0

  def __init__(self, contents=None):
    self.histogram_ = ImagesHistogram()
    if contents is not None: self.MergeFromString(contents)

  def histogram(self): return self.histogram_

  def mutable_histogram(self): self.has_histogram_ = 1; return self.histogram_

  def clear_histogram(self):self.has_histogram_ = 0; self.histogram_.Clear()

  def has_histogram(self): return self.has_histogram_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_histogram()): self.mutable_histogram().MergeFrom(x.histogram())

  def Equals(self, x):
    if x is self: return 1
    if self.has_histogram_ != x.has_histogram_: return 0
    if self.has_histogram_ and self.histogram_ != x.histogram_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_histogram_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: histogram not set.')
    elif not self.histogram_.IsInitialized(debug_strs): initialized = 0
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(self.histogram_.ByteSize())
    return n + 1

  def Clear(self):
    self.clear_histogram()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putVarInt32(self.histogram_.ByteSize())
    self.histogram_.OutputUnchecked(out)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.mutable_histogram().TryMerge(tmp)
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_histogram_:
      res+=prefix+"histogram <\n"
      res+=self.histogram_.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  khistogram = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "histogram",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class ImagesGetUrlBaseRequest(ProtocolBuffer.ProtocolMessage):
  has_blob_key_ = 0
  blob_key_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def blob_key(self): return self.blob_key_

  def set_blob_key(self, x):
    self.has_blob_key_ = 1
    self.blob_key_ = x

  def clear_blob_key(self):
    if self.has_blob_key_:
      self.has_blob_key_ = 0
      self.blob_key_ = ""

  def has_blob_key(self): return self.has_blob_key_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_blob_key()): self.set_blob_key(x.blob_key())

  def Equals(self, x):
    if x is self: return 1
    if self.has_blob_key_ != x.has_blob_key_: return 0
    if self.has_blob_key_ and self.blob_key_ != x.blob_key_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_blob_key_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: blob_key not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.blob_key_))
    return n + 1

  def Clear(self):
    self.clear_blob_key()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.blob_key_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_blob_key(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_blob_key_: res+=prefix+("blob_key: %s\n" % self.DebugFormatString(self.blob_key_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kblob_key = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "blob_key",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
class ImagesGetUrlBaseResponse(ProtocolBuffer.ProtocolMessage):
  has_url_ = 0
  url_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def url(self): return self.url_

  def set_url(self, x):
    self.has_url_ = 1
    self.url_ = x

  def clear_url(self):
    if self.has_url_:
      self.has_url_ = 0
      self.url_ = ""

  def has_url(self): return self.has_url_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_url()): self.set_url(x.url())

  def Equals(self, x):
    if x is self: return 1
    if self.has_url_ != x.has_url_: return 0
    if self.has_url_ and self.url_ != x.url_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_url_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: url not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.url_))
    return n + 1

  def Clear(self):
    self.clear_url()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.url_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_url(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_url_: res+=prefix+("url: %s\n" % self.DebugFormatString(self.url_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kurl = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "url",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""

__all__ = ['ImagesServiceError','ImagesServiceTransform','Transform','ImageData','OutputSettings','ImagesTransformRequest','ImagesTransformResponse','CompositeImageOptions','ImagesCanvas','ImagesCompositeRequest','ImagesCompositeResponse','ImagesHistogramRequest','ImagesHistogram','ImagesHistogramResponse','ImagesGetUrlBaseRequest','ImagesGetUrlBaseResponse']
