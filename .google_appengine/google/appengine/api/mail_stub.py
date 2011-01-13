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

"""Stub version of the mail API, writes email to logs and can optionally
send real email via SMTP or sendmail."""





from email import MIMEBase
from email import MIMEMultipart
from email import MIMEText
import logging
import mail
import mimetypes
import subprocess
import smtplib

from google.appengine.api import apiproxy_stub


MAX_REQUEST_SIZE = 32 << 20


class MailServiceStub(apiproxy_stub.APIProxyStub):
  """Python only mail service stub.

  This stub does not actually attempt to send email.  instead it merely logs
  a description of the email to the developers console.

  Args:
    host: Host of SMTP server to use.  Blank disables sending SMTP.
    port: Port of SMTP server to use.
    user: User to log in to SMTP server as.
    password: Password for SMTP server user.
  """

  def __init__(self,
               host=None,
               port=25,
               user='',
               password='',
               enable_sendmail=False,
               show_mail_body=False,
               service_name='mail'):
    """Constructor.

    Args:
      host: Host of SMTP mail server.
      post: Port of SMTP mail server.
      user: Sending user of SMTP mail.
      password: SMTP password.
      enable_sendmail: Whether sendmail enabled or not.
      show_mail_body: Whether to show mail body in log.
      service_name: Service name expected for all calls.
    """
    super(MailServiceStub, self).__init__(service_name,
                                          max_request_size=MAX_REQUEST_SIZE)
    self._smtp_host = host
    self._smtp_port = port
    self._smtp_user = user
    self._smtp_password = password
    self._enable_sendmail = enable_sendmail
    self._show_mail_body = show_mail_body

  def _GenerateLog(self, method, message, log):
    """Generate a list of log messages representing sent mail.

    Args:
      message: Message to write to log.
      log: Log function of type string -> None
    """
    log('MailService.%s' % method)
    log('  From: %s' % message.sender())

    for address in message.to_list():
      log('  To: %s' % address)
    for address in message.cc_list():
      log('  Cc: %s' % address)
    for address in message.bcc_list():
      log('  Bcc: %s' % address)

    if message.replyto():
      log('  Reply-to: %s' % message.replyto())

    log('  Subject: %s' % message.subject())

    if message.has_textbody():
      log('  Body:')
      log('    Content-type: text/plain')
      log('    Data length: %d' % len(message.textbody()))
      if self._show_mail_body:
        log('-----\n' + message.textbody() + '\n-----')

    if message.has_htmlbody():
      log('  Body:')
      log('    Content-type: text/html')
      log('    Data length: %d' % len(message.htmlbody()))
      if self._show_mail_body:
        log('-----\n' + message.htmlbody() + '\n-----')

    for attachment in message.attachment_list():
      log('  Attachment:')
      log('    File name: %s' % attachment.filename())
      log('    Data length: %s' % len(attachment.data()))

  def _SendSMTP(self, mime_message, smtp_lib=smtplib.SMTP):
    """Send MIME message via SMTP.

    Connects to SMTP server and sends MIME message.  If user is supplied
    will try to login to that server to send as authenticated.  Does not
    currently support encryption.

    Args:
      mime_message: MimeMessage to send.  Create using ToMIMEMessage.
      smtp_lib: Class of SMTP library.  Used for dependency injection.
    """
    smtp = smtp_lib()
    try:
      smtp.connect(self._smtp_host, self._smtp_port)
      if self._smtp_user:
        smtp.login(self._smtp_user, self._smtp_password)

      tos = ', '.join([mime_message[to] for to in ['To', 'Cc', 'Bcc']
                       if mime_message[to]])
      smtp.sendmail(mime_message['From'], tos, str(mime_message))
    finally:
      smtp.quit()

  def _SendSendmail(self, mime_message,
                    popen=subprocess.Popen,
                    sendmail_command='sendmail'):
    """Send MIME message via sendmail, if exists on computer.

    Attempts to send email via sendmail.  Any IO failure, including
    the program not being found is ignored.

    Args:
      mime_message: MimeMessage to send.  Create using ToMIMEMessage.
      popen: popen function to create a new sub-process.
    """
    try:
      tos = [mime_message[to] for to in ['To', 'Cc', 'Bcc'] if mime_message[to]]
      sendmail_command = '%s %s' % (sendmail_command, ' '.join(tos))

      try:
        child = popen(sendmail_command,
                      shell=True,
                      stdin=subprocess.PIPE,
                      stdout=subprocess.PIPE)
      except (IOError, OSError), e:
        logging.error('Unable to open pipe to sendmail')
        raise
      try:
        child.stdin.write(str(mime_message))
        child.stdin.close()
      finally:
        while child.poll() is None:
          child.stdout.read(100)
        child.stdout.close()
    except (IOError, OSError), e:
      logging.error('Error sending mail using sendmail: ' + str(e))

  def _Send(self, request, response, log=logging.info,
            smtp_lib=smtplib.SMTP,
            popen=subprocess.Popen,
            sendmail_command='sendmail'):
    """Implementation of MailServer::Send().

    Logs email message.  Contents of attachments are not shown, only
    their sizes.  If SMTP is configured, will send via SMTP, else
    will use Sendmail if it is installed.

    Args:
      request: The message to send, a SendMailRequest.
      response: The send response, a SendMailResponse.
      log: Log function to send log information.  Used for dependency
        injection.
      smtp_lib: Class of SMTP library.  Used for dependency injection.
      popen2: popen2 function to use for opening pipe to other process.
        Used for dependency injection.
    """
    self._GenerateLog('Send', request, log)

    if self._smtp_host and self._enable_sendmail:
      log('Both SMTP and sendmail are enabled.  Ignoring sendmail.')

    import email

    mime_message = mail.MailMessageToMIMEMessage(request)
    if self._smtp_host:
      self._SendSMTP(mime_message, smtp_lib)
    elif self._enable_sendmail:
      self._SendSendmail(mime_message, popen, sendmail_command)
    else:
      logging.info('You are not currently sending out real email.  '
                   'If you have sendmail installed you can use it '
                   'by using the server with --enable_sendmail')

  _Dynamic_Send = _Send

  def _SendToAdmins(self, request, response, log=logging.info):
    """Implementation of MailServer::SendToAdmins().

    Logs email message.  Contents of attachments are not shown, only
    their sizes.

    Given the difficulty of determining who the actual sender
    is, Sendmail and SMTP are disabled for this action.

    Args:
      request: The message to send, a SendMailRequest.
      response: The send response, a SendMailResponse.
      log: Log function to send log information.  Used for dependency
        injection.
    """
    self._GenerateLog('SendToAdmins', request, log)

    if self._smtp_host and self._enable_sendmail:
      log('Both SMTP and sendmail are enabled.  Ignoring sendmail.')

  _Dynamic_SendToAdmins = _SendToAdmins
