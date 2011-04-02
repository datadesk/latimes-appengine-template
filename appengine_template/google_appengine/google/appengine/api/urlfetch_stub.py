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






"""Stub version of the urlfetch API, based on httplib."""



_successfully_imported_fancy_urllib = False
_fancy_urllib_InvalidCertException = None
_fancy_urllib_SSLError = None
try:
  import fancy_urllib
  _successfully_imported_fancy_urllib = True
  _fancy_urllib_InvalidCertException = fancy_urllib.InvalidCertificateException
  _fancy_urllib_SSLError = fancy_urllib.SSLError
except ImportError:
  pass

import gzip
import httplib
import logging
import os
import socket
import StringIO
import urllib
import urlparse

from google.appengine.api import apiproxy_stub
from google.appengine.api import urlfetch
from google.appengine.api import urlfetch_errors
from google.appengine.api import urlfetch_service_pb
from google.appengine.runtime import apiproxy_errors


MAX_RESPONSE_SIZE = 2 ** 25

MAX_REDIRECTS = urlfetch.MAX_REDIRECTS

REDIRECT_STATUSES = frozenset([
  httplib.MOVED_PERMANENTLY,
  httplib.FOUND,
  httplib.SEE_OTHER,
  httplib.TEMPORARY_REDIRECT,
])





_API_CALL_DEADLINE = 5.0




_API_CALL_VALIDATE_CERTIFICATE_DEFAULT = True







_UNTRUSTED_REQUEST_HEADERS = frozenset([
  'content-length',
  'host',
  'vary',
  'via',
  'x-forwarded-for',
])


def _CanValidateCerts():
  return (_successfully_imported_fancy_urllib and
          fancy_urllib.can_validate_certs())


def _SetupSSL(path):
  global CERT_PATH
  if os.path.exists(path):
    CERT_PATH = path
  else:
    CERT_PATH = None
    logging.warning('%s missing; without this urlfetch will not be able to '
                    'validate SSL certificates.', path)

  if not _CanValidateCerts():
    logging.warning('No ssl package found. urlfetch will not be able to '
                    'validate SSL certificates.')


_SetupSSL(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..',
                                        '..', 'lib', 'cacerts',
                                        'urlfetch_cacerts.txt')))

def _IsAllowedPort(port):

  if port is None:
    return True
  try:
    port = int(port)
  except ValueError, e:
    return False




  if ((port >= 80 and port <= 90) or
      (port >= 440 and port <= 450) or
      port >= 1024):
    return True
  return False


class URLFetchServiceStub(apiproxy_stub.APIProxyStub):
  """Stub version of the urlfetch API to be used with apiproxy_stub_map."""

  def __init__(self, service_name='urlfetch'):
    """Initializer.

    Args:
      service_name: Service name expected for all calls.
    """
    super(URLFetchServiceStub, self).__init__(service_name)

  def _Dynamic_Fetch(self, request, response):
    """Trivial implementation of URLFetchService::Fetch().

    Args:
      request: the fetch to perform, a URLFetchRequest
      response: the fetch response, a URLFetchResponse
    """
    (protocol, host, path, parameters, query, fragment) = urlparse.urlparse(request.url())

    payload = None
    if request.method() == urlfetch_service_pb.URLFetchRequest.GET:
      method = 'GET'
    elif request.method() == urlfetch_service_pb.URLFetchRequest.POST:
      method = 'POST'
      payload = request.payload()
    elif request.method() == urlfetch_service_pb.URLFetchRequest.HEAD:
      method = 'HEAD'
    elif request.method() == urlfetch_service_pb.URLFetchRequest.PUT:
      method = 'PUT'
      payload = request.payload()
    elif request.method() == urlfetch_service_pb.URLFetchRequest.DELETE:
      method = 'DELETE'
    else:
      logging.error('Invalid method: %s', request.method())
      raise apiproxy_errors.ApplicationError(
        urlfetch_service_pb.URLFetchServiceError.UNSPECIFIED_ERROR)

    if not (protocol == 'http' or protocol == 'https'):
      logging.error('Invalid protocol: %s', protocol)
      raise apiproxy_errors.ApplicationError(
        urlfetch_service_pb.URLFetchServiceError.INVALID_URL)

    if not host:
      logging.error('Missing host.')


      raise apiproxy_errors.ApplicationError(
          urlfetch_service_pb.URLFetchServiceError.FETCH_ERROR)

    sanitized_headers = self._SanitizeHttpHeaders(_UNTRUSTED_REQUEST_HEADERS,
                                                  request.header_list())
    request.clear_header()
    request.header_list().extend(sanitized_headers)
    deadline = _API_CALL_DEADLINE
    if request.has_deadline():
      deadline = request.deadline()
    validate_certificate = _API_CALL_VALIDATE_CERTIFICATE_DEFAULT
    if request.has_mustvalidateservercertificate():
      validate_certificate = request.mustvalidateservercertificate()

    self._RetrieveURL(request.url(), payload, method,
                      request.header_list(), request, response,
                      follow_redirects=request.followredirects(),
                      deadline=deadline,
                      validate_certificate=validate_certificate)

  def _RetrieveURL(self, url, payload, method, headers, request, response,
                   follow_redirects=True, deadline=_API_CALL_DEADLINE,
                   validate_certificate=_API_CALL_VALIDATE_CERTIFICATE_DEFAULT):
    """Retrieves a URL.

    Args:
      url: String containing the URL to access.
      payload: Request payload to send, if any; None if no payload.
      method: HTTP method to use (e.g., 'GET')
      headers: List of additional header objects to use for the request.
      request: Request object from original request.
      response: Response object to populate with the response data.
      follow_redirects: optional setting (defaulting to True) for whether or not
        we should transparently follow redirects (up to MAX_REDIRECTS)
      deadline: Number of seconds to wait for the urlfetch to finish.
      validate_certificate: If true, do not send request to server unless the
        certificate is valid, signed by a trusted CA and the hostname matches
        the certificate.

    Raises:
      Raises an apiproxy_errors.ApplicationError exception with FETCH_ERROR
      in cases where:
        - MAX_REDIRECTS is exceeded
        - The protocol of the redirected URL is bad or missing.
    """
    last_protocol = ''
    last_host = ''

    for redirect_number in xrange(MAX_REDIRECTS + 1):
      parsed = urlparse.urlparse(url)
      protocol, host, path, parameters, query, fragment = parsed







      port = urllib.splitport(urllib.splituser(host)[1])[1]

      if not _IsAllowedPort(port):
        logging.warning(
          'urlfetch received %s ; port %s is not allowed in production!' %
          (url, port))

      if protocol and not host:

        logging.error('Missing host on redirect; target url is %s' % url)
        raise apiproxy_errors.ApplicationError(
          urlfetch_service_pb.URLFetchServiceError.FETCH_ERROR)




      if not host and not protocol:
        host = last_host
        protocol = last_protocol






      adjusted_headers = {
          'User-Agent':
          'AppEngine-Google; (+http://code.google.com/appengine)',
          'Host': host,
          'Accept-Encoding': 'gzip',
      }
      if payload is not None:
        adjusted_headers['Content-Length'] = len(payload)
      if method == 'POST' and payload:
        adjusted_headers['Content-Type'] = 'application/x-www-form-urlencoded'

      for header in headers:
        if header.key().title().lower() == 'user-agent':
          adjusted_headers['User-Agent'] = (
              '%s %s' %
              (header.value(), adjusted_headers['User-Agent']))
        else:
          adjusted_headers[header.key().title()] = header.value()

      if payload is not None:
        escaped_payload = payload.encode('string_escape')
      else:
        escaped_payload = payload
      logging.debug('Making HTTP request: host = %s, '
                    'url = %s, payload = %s, headers = %s',
                    host, url, escaped_payload, adjusted_headers)
      try:
        if protocol == 'http':
          connection = httplib.HTTPConnection(host)
        elif protocol == 'https':
          if (validate_certificate and _CanValidateCerts() and
              CERT_PATH):

            connection_class = fancy_urllib.create_fancy_connection(
                ca_certs=CERT_PATH)
            connection = connection_class(host)
          else:
            connection = httplib.HTTPSConnection(host)
        else:

          error_msg = 'Redirect specified invalid protocol: "%s"' % protocol
          logging.error(error_msg)
          raise apiproxy_errors.ApplicationError(
              urlfetch_service_pb.URLFetchServiceError.FETCH_ERROR, error_msg)



        last_protocol = protocol
        last_host = host

        if query != '':
          full_path = path + '?' + query
        else:
          full_path = path

        orig_timeout = socket.getdefaulttimeout()
        try:
          socket.setdefaulttimeout(deadline)
          connection.request(method, full_path, payload, adjusted_headers)
          http_response = connection.getresponse()
          if method == 'HEAD':
            http_response_data = ''
          else:
            http_response_data = http_response.read()
        finally:
          socket.setdefaulttimeout(orig_timeout)
          connection.close()
      except (_fancy_urllib_InvalidCertException,
              _fancy_urllib_SSLError), e:
        raise apiproxy_errors.ApplicationError(
          urlfetch_service_pb.URLFetchServiceError.SSL_CERTIFICATE_ERROR,
          str(e))
      except (httplib.error, socket.error, IOError), e:
        raise apiproxy_errors.ApplicationError(
          urlfetch_service_pb.URLFetchServiceError.FETCH_ERROR, str(e))




      if http_response.status in REDIRECT_STATUSES and follow_redirects:

        url = http_response.getheader('Location', None)
        if url is None:
          error_msg = 'Redirecting response was missing "Location" header'
          logging.error(error_msg)
          raise apiproxy_errors.ApplicationError(
              urlfetch_service_pb.URLFetchServiceError.FETCH_ERROR, error_msg)
      else:
        response.set_statuscode(http_response.status)
        if http_response.getheader('content-encoding') == 'gzip':
          gzip_stream = StringIO.StringIO(http_response_data)
          gzip_file = gzip.GzipFile(fileobj=gzip_stream)
          http_response_data = gzip_file.read()
        response.set_content(http_response_data[:MAX_RESPONSE_SIZE])
        for header_key, header_value in http_response.getheaders():
          if (header_key.lower() == 'content-encoding' and
              header_value == 'gzip'):
            continue
          if header_key.lower() == 'content-length':
            header_value = str(len(response.content()))
          header_proto = response.add_header()
          header_proto.set_key(header_key)
          header_proto.set_value(header_value)

        if len(http_response_data) > MAX_RESPONSE_SIZE:
          response.set_contentwastruncated(True)



        if request.url() != url:
          response.set_finalurl(url)


        break
    else:
      error_msg = 'Too many repeated redirects'
      logging.error(error_msg)
      raise apiproxy_errors.ApplicationError(
          urlfetch_service_pb.URLFetchServiceError.FETCH_ERROR, error_msg)

  def _SanitizeHttpHeaders(self, untrusted_headers, headers):
    """Cleans "unsafe" headers from the HTTP request/response.

    Args:
      untrusted_headers: set of untrusted headers names
      headers: list of string pairs, first is header name and the second is header's value
    """
    prohibited_headers = [h.key() for h in headers
                          if h.key().lower() in untrusted_headers]
    if prohibited_headers:
      logging.warn('Stripped prohibited headers from URLFetch request: %s',
                   prohibited_headers)
    return (h for h in headers if h.key().lower() not in untrusted_headers)
