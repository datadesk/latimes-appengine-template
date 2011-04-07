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



"""Runs a development application server for an application.

%(script)s [options] <application root>

Application root must be the path to the application to run in this server.
Must contain a valid app.yaml or app.yml file.

Options:
  --help, -h                 View this helpful message.
  --debug, -d                Use debug logging. (Default false)
  --clear_datastore, -c      Clear the Datastore on startup. (Default false)
  --clear_prospective_search Clear the Prospective Search subscription index
                             (Default false).
  --address=ADDRESS, -a ADDRESS
                             Address to which this server should bind. (Default
                             %(address)s).
  --port=PORT, -p PORT       Port for the server to run on. (Default %(port)s)
  --blobstore_path=DIR       Path to directory to use for storing Blobstore
                             file stub data.
  --datastore_path=DS_FILE   Path to file to use for storing Datastore file
                             stub data.
                             (Default %(datastore_path)s)
  --skip_sdk_update_check    Skip checking for SDK updates. If false, fall back
                             to opt_in setting specified in .appcfg_nag
                             (Default false)
  --use_sqlite               Use the new, SQLite based datastore stub.
                             (Default false)
  --history_path=PATH        Path to use for storing Datastore history.
                             (Default %(history_path)s)
  --require_indexes          Disallows queries that require composite indexes
                             not defined in index.yaml.
  --smtp_host=HOSTNAME       SMTP host to send test mail to.  Leaving this
                             unset will disable SMTP mail sending.
                             (Default '%(smtp_host)s')
  --smtp_port=PORT           SMTP port to send test mail to.
                             (Default %(smtp_port)s)
  --smtp_user=USER           SMTP user to connect as.  Stub will only attempt
                             to login if this field is non-empty.
                             (Default '%(smtp_user)s').
  --smtp_password=PASSWORD   Password for SMTP server.
                             (Default '%(smtp_password)s')
  --rdbms_sqlite_path=PATH   Path to the sqlite3 file for the RDBMS API.
  --mysql_host=HOSTNAME      MySQL database host that the rdbms API will use.
                             (Default '%(mysql_host)s')
  --mysql_port=PORT          MySQL port to connect to.
                             (Default %(mysql_port)s)
  --mysql_user=USER          MySQL user to connect as.
                             (Default %(mysql_user)s)
  --mysql_password=PASSWORD  MySQL password to use.
                             (Default '%(mysql_password)s')
  --mysql_socket=PATH        MySQL Unix socket file path.
                             (Default '%(mysql_socket)s')
  --enable_sendmail          Enable sendmail when SMTP not configured.
                             (Default false)
  --show_mail_body           Log the body of emails in mail stub.
                             (Default false)
  --auth_domain              Authorization domain that this app runs in.
                             (Default gmail.com)
  --debug_imports            Enables debug logging for module imports, showing
                             search paths used for finding modules and any
                             errors encountered during the import process.
  --allow_skipped_files      Allow access to files matched by app.yaml's
                             skipped_files (default False)
  --disable_static_caching   Never allow the browser to cache static files.
                             (Default enable if expiration set in app.yaml)
  --disable_task_running     When supplied, tasks will not be automatically
                             run after submission and must be run manually
                             in the local admin console.
  --task_retry_seconds       How long to wait in seconds before retrying a
                             task after it fails during execution.
                             (Default '%(task_retry_seconds)s')
"""







from google.appengine.tools import os_compat

import getopt
import logging
import os
import signal
import sys
import traceback
import tempfile




logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-8s %(asctime)s %(filename)s:%(lineno)s] %(message)s')

from google.appengine.api import yaml_errors
from google.appengine.dist import py_zipimport
from google.appengine.tools import appcfg
from google.appengine.tools import appengine_rpc
from google.appengine.tools import dev_appserver





DEFAULT_ADMIN_CONSOLE_SERVER = 'appengine.google.com'


ARG_ADDRESS = 'address'
ARG_ADMIN_CONSOLE_SERVER = 'admin_console_server'
ARG_ADMIN_CONSOLE_HOST = 'admin_console_host'
ARG_AUTH_DOMAIN = 'auth_domain'
ARG_CLEAR_DATASTORE = 'clear_datastore'
ARG_BLOBSTORE_PATH = 'blobstore_path'
ARG_DATASTORE_PATH = 'datastore_path'
ARG_PROSPECTIVE_SEARCH_PATH = 'prospective_search_path'
ARG_CLEAR_PROSPECTIVE_SEARCH = 'clear_prospective_search'
ARG_SKIP_SDK_UPDATE_CHECK = 'skip_sdk_update_check'
ARG_USE_SQLITE = 'use_sqlite'
ARG_DEBUG_IMPORTS = 'debug_imports'
ARG_ENABLE_SENDMAIL = 'enable_sendmail'
ARG_SHOW_MAIL_BODY = 'show_mail_body'
ARG_HISTORY_PATH = 'history_path'
ARG_LOGIN_URL = 'login_url'
ARG_LOG_LEVEL = 'log_level'
ARG_PORT = 'port'
ARG_REQUIRE_INDEXES = 'require_indexes'
ARG_ALLOW_SKIPPED_FILES = 'allow_skipped_files'
ARG_SMTP_HOST = 'smtp_host'
ARG_SMTP_PASSWORD = 'smtp_password'
ARG_SMTP_PORT = 'smtp_port'
ARG_SMTP_USER = 'smtp_user'
ARG_RDBMS_SQLITE_PATH = 'rdbms_sqlite_path'
ARG_MYSQL_HOST = 'mysql_host'
ARG_MYSQL_PORT = 'mysql_port'
ARG_MYSQL_USER = 'mysql_user'
ARG_MYSQL_PASSWORD = 'mysql_password'
ARG_MYSQL_SOCKET = 'mysql_socket'
ARG_STATIC_CACHING = 'static_caching'
ARG_TEMPLATE_DIR = 'template_dir'
ARG_DISABLE_TASK_RUNNING = 'disable_task_running'
ARG_TASK_RETRY_SECONDS = 'task_retry_seconds'


ARG_TRUSTED = 'trusted'

SDK_PATH = os.path.dirname(
             os.path.dirname(
               os.path.dirname(
                 os.path.dirname(os_compat.__file__)
               )
             )
           )

DEFAULT_ARGS = {
  ARG_PORT: 8080,
  ARG_LOG_LEVEL: logging.INFO,
  ARG_BLOBSTORE_PATH: os.path.join(tempfile.gettempdir(),
                                   'dev_appserver.blobstore'),
  ARG_DATASTORE_PATH: os.path.join(tempfile.gettempdir(),
                                   'dev_appserver.datastore'),
  ARG_PROSPECTIVE_SEARCH_PATH: os.path.join(tempfile.gettempdir(),
                                 'dev_appserver.prospective_search'),
  ARG_SKIP_SDK_UPDATE_CHECK: False,
  ARG_USE_SQLITE: False,
  ARG_HISTORY_PATH: os.path.join(tempfile.gettempdir(),
                                 'dev_appserver.datastore.history'),
  ARG_LOGIN_URL: '/_ah/login',
  ARG_CLEAR_DATASTORE: False,
  ARG_CLEAR_PROSPECTIVE_SEARCH: False,
  ARG_REQUIRE_INDEXES: False,
  ARG_TEMPLATE_DIR: os.path.join(SDK_PATH, 'templates'),
  ARG_SMTP_HOST: '',
  ARG_SMTP_PORT: 25,
  ARG_SMTP_USER: '',
  ARG_SMTP_PASSWORD: '',
  ARG_RDBMS_SQLITE_PATH: os.path.join(tempfile.gettempdir(),
                                      'dev_appserver.rdbms'),
  ARG_MYSQL_HOST: 'localhost',
  ARG_MYSQL_PORT: 3306,
  ARG_MYSQL_USER: '',
  ARG_MYSQL_PASSWORD: '',
  ARG_MYSQL_SOCKET: '',
  ARG_ENABLE_SENDMAIL: False,
  ARG_SHOW_MAIL_BODY: False,
  ARG_AUTH_DOMAIN: 'gmail.com',
  ARG_ADDRESS: 'localhost',
  ARG_ADMIN_CONSOLE_SERVER: DEFAULT_ADMIN_CONSOLE_SERVER,
  ARG_ADMIN_CONSOLE_HOST: None,
  ARG_ALLOW_SKIPPED_FILES: False,
  ARG_STATIC_CACHING: True,
  ARG_DISABLE_TASK_RUNNING: False,
  ARG_TASK_RETRY_SECONDS: 30,
  ARG_TRUSTED: False,
}


def PrintUsageExit(code):
  """Prints usage information and exits with a status code.

  Args:
    code: Status code to pass to sys.exit() after displaying usage information.
  """
  render_dict = DEFAULT_ARGS.copy()
  render_dict['script'] = os.path.basename(sys.argv[0])
  print sys.modules['__main__'].__doc__ % render_dict
  sys.stdout.flush()
  sys.exit(code)


def ParseArguments(argv):
  """Parses command-line arguments.

  Args:
    argv: Command-line arguments, including the executable name, used to
      execute this application.

  Returns:
    Tuple (args, option_dict) where:
      args: List of command-line arguments following the executable name.
      option_dict: Dictionary of parsed flags that maps keys from DEFAULT_ARGS
        to their values, which are either pulled from the defaults, or from
        command-line flags.
  """
  option_dict = DEFAULT_ARGS.copy()

  try:
    opts, args = getopt.gnu_getopt(
      argv[1:],
      'a:cdhp:',
      [ 'address=',
        'admin_console_server=',
        'admin_console_host=',
        'allow_skipped_files',
        'auth_domain=',
        'clear_datastore',
        'clear_prospective_search',
        'blobstore_path=',
        'datastore_path=',
        'skip_sdk_update_check',
        'use_sqlite',
        'debug',
        'debug_imports',
        'enable_sendmail',
        'disable_static_caching',
        'show_mail_body',
        'help',
        'history_path=',
        'rdbms_sqlite_path=',
        'mysql_host=',
        'mysql_port=',
        'mysql_user=',
        'mysql_password=',
        'mysql_socket=',
        'port=',
        'require_indexes',
        'smtp_host=',
        'smtp_password=',
        'smtp_port=',
        'smtp_user=',
        'disable_task_running',
        'task_retry_seconds=',
        'template_dir=',
        'trusted',
      ])
  except getopt.GetoptError, e:
    print >>sys.stderr, 'Error: %s' % e
    PrintUsageExit(1)

  for option, value in opts:
    if option in ('-h', '--help'):
      PrintUsageExit(0)

    if option in ('-d', '--debug'):
      option_dict[ARG_LOG_LEVEL] = logging.DEBUG

    if option in ('-p', '--port'):
      try:
        option_dict[ARG_PORT] = int(value)
        if not (65535 > option_dict[ARG_PORT] > 0):
          raise ValueError
      except ValueError:
        print >>sys.stderr, 'Invalid value supplied for port'
        PrintUsageExit(1)

    if option in ('-a', '--address'):
      option_dict[ARG_ADDRESS] = value

    if option == '--blobstore_path':
      option_dict[ARG_BLOBSTORE_PATH] = os.path.abspath(value)

    if option == '--datastore_path':
      option_dict[ARG_DATASTORE_PATH] = os.path.abspath(value)

    if option == '--prospective_search_path':
      option_dict[ARG_PROSPECTIVE_SEARCH_PATH] = os.path.abspath(value)

    if option == '--skip_sdk_update_check':
      option_dict[ARG_SKIP_SDK_UPDATE_CHECK] = True

    if option == '--use_sqlite':
      option_dict[ARG_USE_SQLITE] = True

    if option == '--history_path':
      option_dict[ARG_HISTORY_PATH] = os.path.abspath(value)

    if option in ('-c', '--clear_datastore'):
      option_dict[ARG_CLEAR_DATASTORE] = True

    if option == '--clear_prospective_search':
      option_dict[ARG_CLEAR_PROSPECTIVE_SEARCH] = True

    if option == '--require_indexes':
      option_dict[ARG_REQUIRE_INDEXES] = True

    if option == '--rdbms_sqlite_path':
      option_dict[ARG_RDBMS_SQLITE_PATH] = value

    if option == '--mysql_host':
      option_dict[ARG_MYSQL_HOST] = value

    if option == '--mysql_port':
      option_dict[ARG_MYSQL_PORT] = _ParsePort(value, '--mysql_port')

    if option == '--mysql_user':
      option_dict[ARG_MYSQL_USER] = value

    if option == '--mysql_password':
      option_dict[ARG_MYSQL_PASSWORD] = value

    if option == '--mysql_socket':
      option_dict[ARG_MYSQL_SOCKET] = value

    if option == '--smtp_host':
      option_dict[ARG_SMTP_HOST] = value

    if option == '--smtp_port':
      option_dict[ARG_SMTP_PORT] = _ParsePort(value, '--smtp_port')

    if option == '--smtp_user':
      option_dict[ARG_SMTP_USER] = value

    if option == '--smtp_password':
      option_dict[ARG_SMTP_PASSWORD] = value

    if option == '--enable_sendmail':
      option_dict[ARG_ENABLE_SENDMAIL] = True

    if option == '--show_mail_body':
      option_dict[ARG_SHOW_MAIL_BODY] = True

    if option == '--auth_domain':
      option_dict['_DEFAULT_ENV_AUTH_DOMAIN'] = value

    if option == '--debug_imports':
      option_dict['_ENABLE_LOGGING'] = True

    if option == '--template_dir':
      option_dict[ARG_TEMPLATE_DIR] = value

    if option == '--admin_console_server':
      option_dict[ARG_ADMIN_CONSOLE_SERVER] = value.strip()

    if option == '--admin_console_host':
      option_dict[ARG_ADMIN_CONSOLE_HOST] = value

    if option == '--allow_skipped_files':
      option_dict[ARG_ALLOW_SKIPPED_FILES] = True

    if option == '--disable_static_caching':
      option_dict[ARG_STATIC_CACHING] = False

    if option == '--disable_task_running':
      option_dict[ARG_DISABLE_TASK_RUNNING] = True

    if option == '--task_retry_seconds':
      try:
        option_dict[ARG_TASK_RETRY_SECONDS] = int(value)
        if option_dict[ARG_TASK_RETRY_SECONDS] < 0:
          raise ValueError
      except ValueError:
        print >>sys.stderr, 'Invalid value supplied for task_retry_seconds'
        PrintUsageExit(1)

    if option == '--trusted':
      option_dict[ARG_TRUSTED] = True

  return args, option_dict


def _ParsePort(port, description):
  """Parses a port number from a string.

  Args:
    port: string
    description: string to use in error messages.

  Returns: integer between 0 and 65535

  Raises:
    ValueError if port is not a valid port number.
  """
  try:
    port = int(port)
    if not (65535 > port > 0):
      raise ValueError
    return port
  except ValueError:
    print >>sys.stderr, 'Invalid value %s supplied for %s' % (port, description)
    PrintUsageExit(1)


def MakeRpcServer(option_dict):
  """Create a new HttpRpcServer.

  Creates a new HttpRpcServer to check for updates to the SDK.

  Args:
    option_dict: The dict of command line options.

  Returns:
    A HttpRpcServer.
  """
  server = appengine_rpc.HttpRpcServer(
      option_dict[ARG_ADMIN_CONSOLE_SERVER],
      lambda: ('unused_email', 'unused_password'),
      appcfg.GetUserAgent(),
      appcfg.GetSourceName(),
      host_override=option_dict[ARG_ADMIN_CONSOLE_HOST])

  server.authenticated = True
  return server


def SigTermHandler(signum, frame):
  """Handler for TERM signal.

  Raises a KeyboardInterrupt to perform a graceful shutdown on SIGTERM signal.
  """
  raise KeyboardInterrupt()


def main(argv):
  """Runs the development application server."""
  args, option_dict = ParseArguments(argv)

  if len(args) != 1:
    print >>sys.stderr, 'Invalid arguments'
    PrintUsageExit(1)

  root_path = args[0]

  if '_DEFAULT_ENV_AUTH_DOMAIN' in option_dict:
    auth_domain = option_dict['_DEFAULT_ENV_AUTH_DOMAIN']
    dev_appserver.DEFAULT_ENV['AUTH_DOMAIN'] = auth_domain
  if '_ENABLE_LOGGING' in option_dict:
    enable_logging = option_dict['_ENABLE_LOGGING']
    dev_appserver.HardenedModulesHook.ENABLE_LOGGING = enable_logging

  log_level = option_dict[ARG_LOG_LEVEL]
  port = option_dict[ARG_PORT]
  login_url = option_dict[ARG_LOGIN_URL]
  template_dir = option_dict[ARG_TEMPLATE_DIR]
  serve_address = option_dict[ARG_ADDRESS]
  require_indexes = option_dict[ARG_REQUIRE_INDEXES]
  allow_skipped_files = option_dict[ARG_ALLOW_SKIPPED_FILES]
  static_caching = option_dict[ARG_STATIC_CACHING]
  skip_sdk_update_check = option_dict[ARG_SKIP_SDK_UPDATE_CHECK]



  option_dict['root_path'] = os.path.realpath(root_path)


  logging.getLogger().setLevel(log_level)

  config = None
  try:
    config, matcher = dev_appserver.LoadAppConfig(root_path, {})
  except yaml_errors.EventListenerError, e:
    logging.error('Fatal error when loading application configuration:\n' +
                  str(e))
    return 1
  except dev_appserver.InvalidAppConfigError, e:
    logging.error('Application configuration file invalid:\n%s', e)
    return 1

  if option_dict[ARG_ADMIN_CONSOLE_SERVER] != '':

    server = MakeRpcServer(option_dict)
    if skip_sdk_update_check:
      logging.info('Skipping update check.')
    else:
      update_check = appcfg.UpdateCheck(server, config)
      update_check.CheckSupportedVersion()
      if update_check.AllowedToCheckForUpdates():
        update_check.CheckForUpdates()

  try:
    dev_appserver.SetupStubs(config.application, **option_dict)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logging.error(str(exc_type) + ': ' + str(exc_value))
    logging.debug(''.join(traceback.format_exception(
          exc_type, exc_value, exc_traceback)))
    return 1

  http_server = dev_appserver.CreateServer(
      root_path,
      login_url,
      port,
      template_dir,
      sdk_dir=SDK_PATH,
      serve_address=serve_address,
      require_indexes=require_indexes,
      allow_skipped_files=allow_skipped_files,
      static_caching=static_caching)

  signal.signal(signal.SIGTERM, SigTermHandler)


  logging.info('Running application %s on port %d: http://%s:%d',
               config.application, port, serve_address, port)
  try:
    try:
      http_server.serve_forever()
    except KeyboardInterrupt:
      logging.info('Server interrupted by user, terminating')
    except:
      exc_info = sys.exc_info()
      info_string = '\n'.join(traceback.format_exception(*exc_info))
      logging.error('Error encountered:\n%s\nNow terminating.', info_string)
      return 1
  finally:
    http_server.server_close()

  return 0



if __name__ == '__main__':
  sys.exit(main(sys.argv))
