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

"""Image manipulation API.

Classes defined in this module:
  Image: class used to encapsulate image information and transformations for
    that image.

    The current manipulations that are available are resize, rotate,
    horizontal_flip, vertical_flip, crop and im_feeling_lucky.

    It should be noted that each transform can only be called once per image
    per execute_transforms() call.
"""



import struct

from google.appengine.api import apiproxy_stub_map
from google.appengine.api.images import images_service_pb
from google.appengine.runtime import apiproxy_errors


JPEG = images_service_pb.OutputSettings.JPEG
PNG = images_service_pb.OutputSettings.PNG

OUTPUT_ENCODING_TYPES = frozenset([JPEG, PNG])

TOP_LEFT = images_service_pb.CompositeImageOptions.TOP_LEFT
TOP_CENTER = images_service_pb.CompositeImageOptions.TOP
TOP_RIGHT = images_service_pb.CompositeImageOptions.TOP_RIGHT
CENTER_LEFT = images_service_pb.CompositeImageOptions.LEFT
CENTER_CENTER = images_service_pb.CompositeImageOptions.CENTER
CENTER_RIGHT = images_service_pb.CompositeImageOptions.RIGHT
BOTTOM_LEFT = images_service_pb.CompositeImageOptions.BOTTOM_LEFT
BOTTOM_CENTER = images_service_pb.CompositeImageOptions.BOTTOM
BOTTOM_RIGHT = images_service_pb.CompositeImageOptions.BOTTOM_RIGHT

ANCHOR_TYPES = frozenset([TOP_LEFT, TOP_CENTER, TOP_RIGHT, CENTER_LEFT,
                          CENTER_CENTER, CENTER_RIGHT, BOTTOM_LEFT,
                          BOTTOM_CENTER, BOTTOM_RIGHT])

MAX_TRANSFORMS_PER_REQUEST = 10

MAX_COMPOSITES_PER_REQUEST = 16


class Error(Exception):
  """Base error class for this module."""


class TransformationError(Error):
  """Error while attempting to transform the image."""


class BadRequestError(Error):
  """The parameters given had something wrong with them."""


class NotImageError(Error):
  """The image data given is not recognizable as an image."""


class BadImageError(Error):
  """The image data given is corrupt."""


class LargeImageError(Error):
  """The image data given is too large to process."""


class InvalidBlobKeyError(Error):
  """The provided blob key was invalid."""


class Image(object):
  """Image object to manipulate."""

  def __init__(self, image_data=None, blob_key=None):
    """Constructor.

    Args:
      image_data: str, image data in string form.
      blob_key: str, image data as a blobstore blob key.

    Raises:
      NotImageError if the given data is empty.
    """
    if not image_data and not blob_key:
      raise NotImageError("Empty image data.")
    if image_data and blob_key:
      raise NotImageError("Can only take one image or blob key.")

    self._image_data = image_data
    self._blob_key = blob_key
    self._transforms = []
    self._width = None
    self._height = None

  def _check_transform_limits(self):
    """Ensure some simple limits on the number of transforms allowed.

    Raises:
      BadRequestError if MAX_TRANSFORMS_PER_REQUEST transforms have already been
      requested for this image
    """
    if len(self._transforms) >= MAX_TRANSFORMS_PER_REQUEST:
      raise BadRequestError("%d transforms have already been requested on this "
                            "image." % MAX_TRANSFORMS_PER_REQUEST)

  def _update_dimensions(self):
    """Updates the width and height fields of the image.

    Raises:
      NotImageError if the image data is not an image.
      BadImageError if the image data is corrupt.
    """
    if not self._image_data:
      raise NotImageError("Dimensions unavailable for blob key input")
    size = len(self._image_data)
    if size >= 6 and self._image_data.startswith("GIF"):
      self._update_gif_dimensions()
    elif size >= 8 and self._image_data.startswith("\x89PNG\x0D\x0A\x1A\x0A"):
      self._update_png_dimensions()
    elif size >= 2 and self._image_data.startswith("\xff\xD8"):
      self._update_jpeg_dimensions()
    elif (size >= 8 and (self._image_data.startswith("II\x2a\x00") or
                         self._image_data.startswith("MM\x00\x2a"))):
      self._update_tiff_dimensions()
    elif size >= 2 and self._image_data.startswith("BM"):
      self._update_bmp_dimensions()
    elif size >= 4 and self._image_data.startswith("\x00\x00\x01\x00"):
      self._update_ico_dimensions()
    else:
      raise NotImageError("Unrecognized image format")

  def _update_gif_dimensions(self):
    """Updates the width and height fields of the gif image.

    Raises:
      BadImageError if the image string is not a valid gif image.
    """
    size = len(self._image_data)
    if size >= 10:
      self._width, self._height = struct.unpack("<HH", self._image_data[6:10])
    else:
      raise BadImageError("Corrupt GIF format")

  def _update_png_dimensions(self):
    """Updates the width and height fields of the png image.

    Raises:
      BadImageError if the image string is not a valid png image.
    """
    size = len(self._image_data)
    if size >= 24 and self._image_data[12:16] == "IHDR":
      self._width, self._height = struct.unpack(">II", self._image_data[16:24])
    else:
      raise BadImageError("Corrupt PNG format")

  def _update_jpeg_dimensions(self):
    """Updates the width and height fields of the jpeg image.

    Raises:
      BadImageError if the image string is not a valid jpeg image.
    """
    size = len(self._image_data)
    offset = 2
    while offset < size:
      while offset < size and ord(self._image_data[offset]) != 0xFF:
        offset += 1
      while offset < size and ord(self._image_data[offset]) == 0xFF:
        offset += 1
      if (offset < size and ord(self._image_data[offset]) & 0xF0 == 0xC0 and
          ord(self._image_data[offset]) != 0xC4):
        offset += 4
        if offset + 4 <= size:
          self._height, self._width = struct.unpack(
              ">HH",
              self._image_data[offset:offset + 4])
          break
        else:
          raise BadImageError("Corrupt JPEG format")
      elif offset + 3 <= size:
        offset += 1
        offset += struct.unpack(">H", self._image_data[offset:offset + 2])[0]
      else:
        raise BadImageError("Corrupt JPEG format")
    if self._height is None or self._width is None:
      raise BadImageError("Corrupt JPEG format")

  def _update_tiff_dimensions(self):
    """Updates the width and height fields of the tiff image.

    Raises:
      BadImageError if the image string is not a valid tiff image.
    """
    size = len(self._image_data)
    if self._image_data.startswith("II"):
      endianness = "<"
    else:
      endianness = ">"
    ifd_offset = struct.unpack(endianness + "I", self._image_data[4:8])[0]
    if ifd_offset + 14 <= size:
      ifd_size = struct.unpack(
          endianness + "H",
          self._image_data[ifd_offset:ifd_offset + 2])[0]
      ifd_offset += 2
      for unused_i in range(0, ifd_size):
        if ifd_offset + 12 <= size:
          tag = struct.unpack(
              endianness + "H",
              self._image_data[ifd_offset:ifd_offset + 2])[0]
          if tag == 0x100 or tag == 0x101:
            value_type = struct.unpack(
                endianness + "H",
                self._image_data[ifd_offset + 2:ifd_offset + 4])[0]
            if value_type == 3:
              format = endianness + "H"
              end_offset = ifd_offset + 10
            elif value_type == 4:
              format = endianness + "I"
              end_offset = ifd_offset + 12
            else:
              format = endianness + "B"
              end_offset = ifd_offset + 9
            if tag == 0x100:
              self._width = struct.unpack(
                  format,
                  self._image_data[ifd_offset + 8:end_offset])[0]
              if self._height is not None:
                break
            else:
              self._height = struct.unpack(
                  format,
                  self._image_data[ifd_offset + 8:end_offset])[0]
              if self._width is not None:
                break
          ifd_offset += 12
        else:
          raise BadImageError("Corrupt TIFF format")
    if self._width is None or self._height is None:
      raise BadImageError("Corrupt TIFF format")

  def _update_bmp_dimensions(self):
    """Updates the width and height fields of the bmp image.

    Raises:
      BadImageError if the image string is not a valid bmp image.
    """
    size = len(self._image_data)
    if size >= 18:
      header_length = struct.unpack("<I", self._image_data[14:18])[0]
      if ((header_length == 40 or header_length == 108 or
           header_length == 124 or header_length == 64) and size >= 26):
        self._width, self._height = struct.unpack("<II",
                                                  self._image_data[18:26])
      elif header_length == 12 and size >= 22:
        self._width, self._height = struct.unpack("<HH",
                                                  self._image_data[18:22])
      else:
        raise BadImageError("Corrupt BMP format")
    else:
      raise BadImageError("Corrupt BMP format")

  def _update_ico_dimensions(self):
    """Updates the width and height fields of the ico image.

    Raises:
      BadImageError if the image string is not a valid ico image.
    """
    size = len(self._image_data)
    if size >= 8:
      self._width, self._height = struct.unpack("<BB", self._image_data[6:8])
      if not self._width:
        self._width = 256
      if not self._height:
        self._height = 256
    else:
      raise BadImageError("Corrupt ICO format")

  def resize(self, width=0, height=0):
    """Resize the image maintaining the aspect ratio.

    If both width and height are specified, the more restricting of the two
    values will be used when resizing the photo.  The maximum dimension allowed
    for both width and height is 4000 pixels.

    Args:
      width: int, width (in pixels) to change the image width to.
      height: int, height (in pixels) to change the image height to.

    Raises:
      TypeError when width or height is not either 'int' or 'long' types.
      BadRequestError when there is something wrong with the given height or
        width or if MAX_TRANSFORMS_PER_REQUEST transforms have already been
        requested on this image.
    """
    if (not isinstance(width, (int, long)) or
        not isinstance(height, (int, long))):
      raise TypeError("Width and height must be integers.")
    if width < 0 or height < 0:
      raise BadRequestError("Width and height must be >= 0.")

    if not width and not height:
      raise BadRequestError("At least one of width or height must be > 0.")

    if width > 4000 or height > 4000:
      raise BadRequestError("Both width and height must be <= 4000.")

    self._check_transform_limits()

    transform = images_service_pb.Transform()
    transform.set_width(width)
    transform.set_height(height)

    self._transforms.append(transform)

  def rotate(self, degrees):
    """Rotate an image a given number of degrees clockwise.

    Args:
      degrees: int, must be a multiple of 90.

    Raises:
      TypeError when degrees is not either 'int' or 'long' types.
      BadRequestError when there is something wrong with the given degrees or
      if MAX_TRANSFORMS_PER_REQUEST transforms have already been requested.
    """
    if not isinstance(degrees, (int, long)):
      raise TypeError("Degrees must be integers.")

    if degrees % 90 != 0:
      raise BadRequestError("degrees argument must be multiple of 90.")

    degrees = degrees % 360

    self._check_transform_limits()

    transform = images_service_pb.Transform()
    transform.set_rotate(degrees)

    self._transforms.append(transform)

  def horizontal_flip(self):
    """Flip the image horizontally.

    Raises:
      BadRequestError if MAX_TRANSFORMS_PER_REQUEST transforms have already been
      requested on the image.
    """
    self._check_transform_limits()

    transform = images_service_pb.Transform()
    transform.set_horizontal_flip(True)

    self._transforms.append(transform)

  def vertical_flip(self):
    """Flip the image vertically.

    Raises:
      BadRequestError if MAX_TRANSFORMS_PER_REQUEST transforms have already been
      requested on the image.
    """
    self._check_transform_limits()
    transform = images_service_pb.Transform()
    transform.set_vertical_flip(True)

    self._transforms.append(transform)

  def _validate_crop_arg(self, val, val_name):
    """Validate the given value of a Crop() method argument.

    Args:
      val: float, value of the argument.
      val_name: str, name of the argument.

    Raises:
      TypeError if the args are not of type 'float'.
      BadRequestError when there is something wrong with the given bounding box.
    """
    if type(val) != float:
      raise TypeError("arg '%s' must be of type 'float'." % val_name)

    if not (0 <= val <= 1.0):
      raise BadRequestError("arg '%s' must be between 0.0 and 1.0 "
                            "(inclusive)" % val_name)

  def crop(self, left_x, top_y, right_x, bottom_y):
    """Crop the image.

    The four arguments are the scaling numbers to describe the bounding box
    which will crop the image.  The upper left point of the bounding box will
    be at (left_x*image_width, top_y*image_height) the lower right point will
    be at (right_x*image_width, bottom_y*image_height).

    Args:
      left_x: float value between 0.0 and 1.0 (inclusive).
      top_y: float value between 0.0 and 1.0 (inclusive).
      right_x: float value between 0.0 and 1.0 (inclusive).
      bottom_y: float value between 0.0 and 1.0 (inclusive).

    Raises:
      TypeError if the args are not of type 'float'.
      BadRequestError when there is something wrong with the given bounding box
        or if MAX_TRANSFORMS_PER_REQUEST transforms have already been requested
        for this image.
    """
    self._validate_crop_arg(left_x, "left_x")
    self._validate_crop_arg(top_y, "top_y")
    self._validate_crop_arg(right_x, "right_x")
    self._validate_crop_arg(bottom_y, "bottom_y")

    if left_x >= right_x:
      raise BadRequestError("left_x must be less than right_x")
    if top_y >= bottom_y:
      raise BadRequestError("top_y must be less than bottom_y")

    self._check_transform_limits()

    transform = images_service_pb.Transform()
    transform.set_crop_left_x(left_x)
    transform.set_crop_top_y(top_y)
    transform.set_crop_right_x(right_x)
    transform.set_crop_bottom_y(bottom_y)

    self._transforms.append(transform)

  def im_feeling_lucky(self):
    """Automatically adjust image contrast and color levels.

    This is similar to the "I'm Feeling Lucky" button in Picasa.

    Raises:
      BadRequestError if MAX_TRANSFORMS_PER_REQUEST transforms have already
        been requested for this image.
    """
    self._check_transform_limits()
    transform = images_service_pb.Transform()
    transform.set_autolevels(True)

    self._transforms.append(transform)

  def _set_imagedata(self, imagedata):
    """Fills in an ImageData PB from this Image instance.

    Args:
      imagedata: An ImageData PB instance
    """
    if self._blob_key:
      imagedata.set_content("")
      imagedata.set_blob_key(self._blob_key)
    else:
      imagedata.set_content(self._image_data)

  def execute_transforms(self, output_encoding=PNG):
    """Perform transformations on given image.

    Args:
      output_encoding: A value from OUTPUT_ENCODING_TYPES.

    Returns:
      str, image data after the transformations have been performed on it.

    Raises:
      BadRequestError when there is something wrong with the request
        specifications.
      NotImageError when the image data given is not an image.
      BadImageError when the image data given is corrupt.
      LargeImageError when the image data given is too large to process.
      InvalidBlobKeyError when the blob key provided is invalid.
      TransformtionError when something errors during image manipulation.
      Error when something unknown, but bad, happens.
    """
    if output_encoding not in OUTPUT_ENCODING_TYPES:
      raise BadRequestError("Output encoding type not in recognized set "
                            "%s" % OUTPUT_ENCODING_TYPES)

    if not self._transforms:
      raise BadRequestError("Must specify at least one transformation.")

    request = images_service_pb.ImagesTransformRequest()
    response = images_service_pb.ImagesTransformResponse()

    self._set_imagedata(request.mutable_image())

    for transform in self._transforms:
      request.add_transform().CopyFrom(transform)

    request.mutable_output().set_mime_type(output_encoding)

    try:
      apiproxy_stub_map.MakeSyncCall("images",
                                     "Transform",
                                     request,
                                     response)
    except apiproxy_errors.ApplicationError, e:
      if (e.application_error ==
          images_service_pb.ImagesServiceError.BAD_TRANSFORM_DATA):
        raise BadRequestError()
      elif (e.application_error ==
            images_service_pb.ImagesServiceError.NOT_IMAGE):
        raise NotImageError()
      elif (e.application_error ==
            images_service_pb.ImagesServiceError.BAD_IMAGE_DATA):
        raise BadImageError()
      elif (e.application_error ==
            images_service_pb.ImagesServiceError.IMAGE_TOO_LARGE):
        raise LargeImageError()
      elif (e.application_error ==
            images_service_pb.ImagesServiceError.INVALID_BLOB_KEY):
        raise InvalidBlobKeyError()
      elif (e.application_error ==
            images_service_pb.ImagesServiceError.UNSPECIFIED_ERROR):
        raise TransformationError()
      else:
        raise Error()

    self._image_data = response.image().content()
    self._blob_key = None
    self._transforms = []
    self._width = None
    self._height = None
    return self._image_data

  @property
  def width(self):
    """Gets the width of the image."""
    if self._width is None:
      self._update_dimensions()
    return self._width

  @property
  def height(self):
    """Gets the height of the image."""
    if self._height is None:
      self._update_dimensions()
    return self._height

  def histogram(self):
    """Calculates the histogram of the image.

    Returns: 3 256-element lists containing the number of occurences of each
    value of each color in the order RGB. As described at
    http://en.wikipedia.org/wiki/Color_histogram for N = 256. i.e. the first
    value of the first list contains the number of pixels with a red value of
    0, the second the number with a red value of 1.

    Raises:
      NotImageError when the image data given is not an image.
      BadImageError when the image data given is corrupt.
      LargeImageError when the image data given is too large to process.
      Error when something unknown, but bad, happens.
    """
    request = images_service_pb.ImagesHistogramRequest()
    response = images_service_pb.ImagesHistogramResponse()

    self._set_imagedata(request.mutable_image())

    try:
      apiproxy_stub_map.MakeSyncCall("images",
                                     "Histogram",
                                     request,
                                     response)
    except apiproxy_errors.ApplicationError, e:
      if (e.application_error ==
          images_service_pb.ImagesServiceError.NOT_IMAGE):
        raise NotImageError()
      elif (e.application_error ==
            images_service_pb.ImagesServiceError.BAD_IMAGE_DATA):
        raise BadImageError()
      elif (e.application_error ==
            images_service_pb.ImagesServiceError.IMAGE_TOO_LARGE):
        raise LargeImageError()
      elif (e.application_error ==
            images_service_pb.ImagesServiceError.INVALID_BLOB_KEY):
        raise InvalidBlobKeyError()
      else:
        raise Error()
    histogram = response.histogram()
    return [histogram.red_list(),
            histogram.green_list(),
            histogram.blue_list()]


def resize(image_data, width=0, height=0, output_encoding=PNG):
  """Resize a given image file maintaining the aspect ratio.

  If both width and height are specified, the more restricting of the two
  values will be used when resizing the photo.  The maximum dimension allowed
  for both width and height is 4000 pixels.

  Args:
    image_data: str, source image data.
    width: int, width (in pixels) to change the image width to.
    height: int, height (in pixels) to change the image height to.
    output_encoding: a value from OUTPUT_ENCODING_TYPES.

  Raises:
    TypeError when width or height not either 'int' or 'long' types.
    BadRequestError when there is something wrong with the given height or
      width.
    Error when something went wrong with the call.  See Image.ExecuteTransforms
      for more details.
  """
  image = Image(image_data)
  image.resize(width, height)
  return image.execute_transforms(output_encoding=output_encoding)


def rotate(image_data, degrees, output_encoding=PNG):
  """Rotate a given image a given number of degrees clockwise.

  Args:
    image_data: str, source image data.
    degrees: value from ROTATE_DEGREE_VALUES.
    output_encoding: a value from OUTPUT_ENCODING_TYPES.

  Raises:
    TypeError when degrees is not either 'int' or 'long' types.
    BadRequestError when there is something wrong with the given degrees.
    Error when something went wrong with the call.  See Image.ExecuteTransforms
      for more details.
  """
  image = Image(image_data)
  image.rotate(degrees)
  return image.execute_transforms(output_encoding=output_encoding)


def horizontal_flip(image_data, output_encoding=PNG):
  """Flip the image horizontally.

  Args:
    image_data: str, source image data.
    output_encoding: a value from OUTPUT_ENCODING_TYPES.

  Raises:
    Error when something went wrong with the call.  See Image.ExecuteTransforms
      for more details.
  """
  image = Image(image_data)
  image.horizontal_flip()
  return image.execute_transforms(output_encoding=output_encoding)


def vertical_flip(image_data, output_encoding=PNG):
  """Flip the image vertically.

  Args:
    image_data: str, source image data.
    output_encoding: a value from OUTPUT_ENCODING_TYPES.

  Raises:
    Error when something went wrong with the call.  See Image.ExecuteTransforms
      for more details.
  """
  image = Image(image_data)
  image.vertical_flip()
  return image.execute_transforms(output_encoding=output_encoding)


def crop(image_data, left_x, top_y, right_x, bottom_y, output_encoding=PNG):
  """Crop the given image.

  The four arguments are the scaling numbers to describe the bounding box
  which will crop the image.  The upper left point of the bounding box will
  be at (left_x*image_width, top_y*image_height) the lower right point will
  be at (right_x*image_width, bottom_y*image_height).

  Args:
    image_data: str, source image data.
    left_x: float value between 0.0 and 1.0 (inclusive).
    top_y: float value between 0.0 and 1.0 (inclusive).
    right_x: float value between 0.0 and 1.0 (inclusive).
    bottom_y: float value between 0.0 and 1.0 (inclusive).
    output_encoding: a value from OUTPUT_ENCODING_TYPES.

  Raises:
    TypeError if the args are not of type 'float'.
    BadRequestError when there is something wrong with the given bounding box.
    Error when something went wrong with the call.  See Image.ExecuteTransforms
      for more details.
  """
  image = Image(image_data)
  image.crop(left_x, top_y, right_x, bottom_y)
  return image.execute_transforms(output_encoding=output_encoding)


def im_feeling_lucky(image_data, output_encoding=PNG):
  """Automatically adjust image levels.

  This is similar to the "I'm Feeling Lucky" button in Picasa.

  Args:
    image_data: str, source image data.
    output_encoding: a value from OUTPUT_ENCODING_TYPES.

  Raises:
    Error when something went wrong with the call.  See Image.ExecuteTransforms
      for more details.
  """
  image = Image(image_data)
  image.im_feeling_lucky()
  return image.execute_transforms(output_encoding=output_encoding)

def composite(inputs, width, height, color=0, output_encoding=PNG):
  """Composite one or more images onto a canvas.

  Args:
    inputs: a list of tuples (image_data, x_offset, y_offset, opacity, anchor)
    where
      image_data: str, source image data.
      x_offset: x offset in pixels from the anchor position
      y_offset: y offset in piyels from the anchor position
      opacity: opacity of the image specified as a float in range [0.0, 1.0]
      anchor: anchoring point from ANCHOR_POINTS. The anchor point of the image
      is aligned with the same anchor point of the canvas. e.g. TOP_RIGHT would
      place the top right corner of the image at the top right corner of the
      canvas then apply the x and y offsets.
    width: canvas width in pixels.
    height: canvas height in pixels.
    color: canvas background color encoded as a 32 bit unsigned int where each
    color channel is represented by one byte in order ARGB.
    output_encoding: a value from OUTPUT_ENCODING_TYPES.

  Returns:
      str, image data of the composited image.

  Raises:
    TypeError If width, height, color, x_offset or y_offset are not of type
    int or long or if opacity is not a float
    BadRequestError If more than MAX_TRANSFORMS_PER_REQUEST compositions have
    been requested, if the canvas width or height is greater than 4000 or less
    than or equal to 0, if the color is invalid or if for any composition
    option, the opacity is outside the range [0,1] or the anchor is invalid.
  """
  if (not isinstance(width, (int, long)) or
      not isinstance(height, (int, long)) or
      not isinstance(color, (int, long))):
    raise TypeError("Width, height and color must be integers.")
  if output_encoding not in OUTPUT_ENCODING_TYPES:
    raise BadRequestError("Output encoding type '%s' not in recognized set "
                          "%s" % (output_encoding, OUTPUT_ENCODING_TYPES))

  if not inputs:
    raise BadRequestError("Must provide at least one input")
  if len(inputs) > MAX_COMPOSITES_PER_REQUEST:
    raise BadRequestError("A maximum of %d composition operations can be"
                          "performed in a single request" %
                          MAX_COMPOSITES_PER_REQUEST)

  if width <= 0 or height <= 0:
    raise BadRequestError("Width and height must be > 0.")
  if width > 4000 or height > 4000:
    raise BadRequestError("Width and height must be <= 4000.")

  if color > 0xffffffff or color < 0:
    raise BadRequestError("Invalid color")
  if color >= 0x80000000:
    color -= 0x100000000

  image_map = {}

  request = images_service_pb.ImagesCompositeRequest()
  response = images_service_pb.ImagesTransformResponse()
  for (image, x, y, opacity, anchor) in inputs:
    if not image:
      raise BadRequestError("Each input must include an image")
    if (not isinstance(x, (int, long)) or
        not isinstance(y, (int, long)) or
        not isinstance(opacity, (float))):
      raise TypeError("x_offset, y_offset must be integers and opacity must"
                      "be a float")
    if x > 4000 or x < -4000:
      raise BadRequestError("xOffsets must be in range [-4000, 4000]")
    if y > 4000 or y < -4000:
      raise BadRequestError("yOffsets must be in range [-4000, 4000]")
    if opacity < 0 or opacity > 1:
      raise BadRequestError("Opacity must be in the range 0.0 to 1.0")
    if anchor not in ANCHOR_TYPES:
      raise BadRequestError("Anchor type '%s' not in recognized set %s" %
                            (anchor, ANCHOR_TYPES))
    if image not in image_map:
      image_map[image] = request.image_size()

      if isinstance(image, Image):
        image._set_imagedata(request.add_image())
      else:
        request.add_image().set_content(image)

    option = request.add_options()
    option.set_x_offset(x)
    option.set_y_offset(y)
    option.set_opacity(opacity)
    option.set_anchor(anchor)
    option.set_source_index(image_map[image])

  request.mutable_canvas().mutable_output().set_mime_type(output_encoding)
  request.mutable_canvas().set_width(width)
  request.mutable_canvas().set_height(height)
  request.mutable_canvas().set_color(color)

  try:
    apiproxy_stub_map.MakeSyncCall("images",
                                   "Composite",
                                   request,
                                   response)
  except apiproxy_errors.ApplicationError, e:
    if (e.application_error ==
        images_service_pb.ImagesServiceError.BAD_TRANSFORM_DATA):
      raise BadRequestError()
    elif (e.application_error ==
          images_service_pb.ImagesServiceError.NOT_IMAGE):
      raise NotImageError()
    elif (e.application_error ==
          images_service_pb.ImagesServiceError.BAD_IMAGE_DATA):
      raise BadImageError()
    elif (e.application_error ==
          images_service_pb.ImagesServiceError.IMAGE_TOO_LARGE):
      raise LargeImageError()
    elif (e.application_error ==
          images_service_pb.ImagesServiceError.INVALID_BLOB_KEY):
      raise InvalidBlobKeyError()
    elif (e.application_error ==
          images_service_pb.ImagesServiceError.UNSPECIFIED_ERROR):
      raise TransformationError()
    else:
      raise Error()

  return response.image().content()


def histogram(image_data):
  """Calculates the histogram of the given image.

  Args:
    image_data: str, source image data.
  Returns: 3 256-element lists containing the number of occurences of each
  value of each color in the order RGB.

  Raises:
    NotImageError when the image data given is not an image.
    BadImageError when the image data given is corrupt.
    LargeImageError when the image data given is too large to process.
    Error when something unknown, but bad, happens.
  """
  image = Image(image_data)
  return image.histogram()
