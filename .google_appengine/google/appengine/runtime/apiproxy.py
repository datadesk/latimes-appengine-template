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

"""Makes API calls to various Google-provided services.

Provides methods for making calls into Google Apphosting services and APIs
from your application code. This code will only work properly from within
the Google Apphosting environment.
"""


import sys
from google.net.proto import ProtocolBuffer
from google.appengine import runtime
from google.appengine.api import apiproxy_rpc
from google3.apphosting.runtime import _apphosting_runtime___python__apiproxy
from google.appengine.runtime import apiproxy_errors

OK                =  0
RPC_FAILED        =  1
CALL_NOT_FOUND    =  2
ARGUMENT_ERROR    =  3
DEADLINE_EXCEEDED =  4
CANCELLED         =  5
APPLICATION_ERROR =  6
OTHER_ERROR       =  7
OVER_QUOTA        =  8
REQUEST_TOO_LARGE =  9
CAPABILITY_DISABLED = 10
FEATURE_DISABLED = 11

_ExceptionsMap = {
  RPC_FAILED:
  (apiproxy_errors.RPCFailedError,
   "The remote RPC to the application server failed for the call %s.%s()."),
  CALL_NOT_FOUND:
  (apiproxy_errors.CallNotFoundError,
   "The API package '%s' or call '%s()' was not found."),
  ARGUMENT_ERROR:
  (apiproxy_errors.ArgumentError,
   "An error occurred parsing (locally or remotely) the arguments to %s.%s()."),
  DEADLINE_EXCEEDED:
  (apiproxy_errors.DeadlineExceededError,
   "The API call %s.%s() took too long to respond and was cancelled."),
  CANCELLED:
  (apiproxy_errors.CancelledError,
   "The API call %s.%s() was explicitly cancelled."),
  OTHER_ERROR:
  (apiproxy_errors.Error,
   "An error occurred for the API request %s.%s()."),
  OVER_QUOTA:
  (apiproxy_errors.OverQuotaError,
  "The API call %s.%s() required more quota than is available."),
  REQUEST_TOO_LARGE:
  (apiproxy_errors.RequestTooLargeError,
  "The request to API call %s.%s() was too large."),









}

class RPC(apiproxy_rpc.RPC):
  """A RPC object, suitable for talking to remote services.

  Each instance of this object can be used only once, and should not be reused.

  Stores the data members and methods for making RPC calls via the APIProxy.
  """

  def __init__(self, *args, **kargs):
    """Constructor for the RPC object. All arguments are optional, and
    simply set members on the class. These data members will be
    overriden by values passed to MakeCall.
    """
    super(RPC, self).__init__(*args, **kargs)
    self.__result_dict = {}

  def _WaitImpl(self):
    """Waits on the API call associated with this RPC. The callback,
    if provided, will be executed before Wait() returns. If this RPC
    is already complete, or if the RPC was never started, this
    function will return immediately.

    Raises:
      InterruptedError if a callback throws an uncaught exception.
    """
    try:
      rpc_completed = _apphosting_runtime___python__apiproxy.Wait(self)
    except (runtime.DeadlineExceededError, apiproxy_errors.InterruptedError):
      raise
    except:
      exc_class, exc, tb = sys.exc_info()
      if (isinstance(exc, SystemError) and
          exc.args[0] == 'uncaught RPC exception'):
        raise
      rpc = None
      if hasattr(exc, "_appengine_apiproxy_rpc"):
        rpc = exc._appengine_apiproxy_rpc
      new_exc = apiproxy_errors.InterruptedError(exc, rpc)
      raise new_exc.__class__, new_exc, tb
    return True

  def _MakeCallImpl(self):
    assert isinstance(self.request, ProtocolBuffer.ProtocolMessage)
    assert isinstance(self.response, ProtocolBuffer.ProtocolMessage)

    e = ProtocolBuffer.Encoder()
    self.request.Output(e)

    self.__state = RPC.RUNNING

    _apphosting_runtime___python__apiproxy.MakeCall(
        self.package, self.call, e.buffer(), self.__result_dict,
        self.__MakeCallDone, self, deadline=(self.deadline or -1))

  def __MakeCallDone(self):
    self.__state = RPC.FINISHING
    self.cpu_usage_mcycles = self.__result_dict['cpu_usage_mcycles']
    if self.__result_dict['error'] == APPLICATION_ERROR:
      self.__exception = apiproxy_errors.ApplicationError(
          self.__result_dict['application_error'],
          self.__result_dict['error_detail'])
    elif self.__result_dict['error'] == CAPABILITY_DISABLED:
      if self.__result_dict['error_detail']:
        self.__exception = apiproxy_errors.CapabilityDisabledError(
            self.__result_dict['error_detail'])
      else:
        self.__exception = apiproxy_errors.CapabilityDisabledError(
            "The API call %s.%s() is temporarily unavailable." % (
            self.package, self.call))
    elif self.__result_dict['error'] == FEATURE_DISABLED:
      self.__exception = apiproxy_errors.FeatureNotEnabledError(
            self.__result_dict['error_detail'])
    elif self.__result_dict['error'] in _ExceptionsMap:
      exception_entry = _ExceptionsMap[self.__result_dict['error']]
      self.__exception = exception_entry[0](
          exception_entry[1] % (self.package, self.call))
    else:
      try:
        self.response.ParseFromString(self.__result_dict['result_string'])
      except Exception, e:
        self.__exception = e
    self.__Callback()

def CreateRPC():
  """Create a RPC instance. suitable for talking to remote services.

  Each RPC instance can be used only once, and should not be reused.

  Returns:
    an instance of RPC object
  """
  return RPC()


def MakeSyncCall(package, call, request, response):
  """Makes a synchronous (i.e. blocking) API call within the specified
  package for the specified call method. request and response must be the
  appropriately typed ProtocolBuffers for the API call. An exception is
  thrown if an error occurs when communicating with the system.

  Args:
    See MakeCall above.

  Raises:
    See CheckSuccess() above.
  """
  rpc = CreateRPC()
  rpc.MakeCall(package, call, request, response)
  rpc.Wait()
  rpc.CheckSuccess()
