# -*- coding: utf-8 -*-
import re
import os
import sys
from optparse import OptionParser

ALLOWED_APPIDS = re.compile('^(?:[a-z\d\-]{1,100}\~)?(?:(?!\-)[a-z\d\-\.]{1,100}:)?(?!-)[a-z\d\-]{1,100}$')

CONFIG_TEMPLATE = """application: %s
version: 1
runtime: python
api_version: 1

handlers:
- url: /remote_api 
  script: $PYTHON_LIB/google/appengine/ext/remote_api/handler.py 
  login: admin

- url: /media
  static_dir: media

- url: /.*
  script: main.py
"""

def execute_from_command_line():
    """
    A command-line utility that will create a virgin Google App Engine
    project enabled to use Django and other helpers.
    
    The first argument is expected to contain the app_id the creator plans
    to register with Google.
    """
    # Configure command line arguments
    parser = OptionParser(
        usage='Usage: startappengineproject [app_id]',
        description='Creates a virgin Google App Engine project enabled to use Django and other helpers.'
        )
    parser.add_option(
        "-p", "--projectname",
        action="store",
        type="string",
        dest="project_name",
        default="project",
        help="Provide a custom name for the project directory that will be created. By default it is 'project'"
    )
    
    # Parse the command line arguments
    (options, args) = parser.parse_args()
    project_name = options.project_name
    try:
        app_id = args[0]
    except IndexError:
         parser.error("You must submit the desired app_id as the first argument")
    
    # Validate the provided app_id
    if not ALLOWED_APPIDS.match(app_id):
        error = "The provided app_id, %s, will not be accepted by Google. " % app_id
        error += "It probably has some underscores or other such things they do not allow."
        parser.error(error)
    
    # Configure target directory setting
    print "Building new app: %s" % app_id
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir[-1] != '/':
        current_dir += '/'
    
    # Check for preexisting project directory
    if os.path.isdir(project_name):
        parser.error("Sorry. Project directory already exists.")
    
    # Copy in the template
    cp = 'cp -R %s ./%s' % (current_dir, project_name)
    print "- " + cp
    os.system(cp)
    
    # Move the SDK to a dot folder
    print "- Moving Google App Engine SDK into a hidden '.' folder"
    mv = 'mv ./%s/google_appengine/ ./%s/.google_appengine/' % (project_name, project_name)
    print "- " + mv
    os.system(mv)
    
    # Load the app_id into the config file
    print "- Configuring app.yaml"
    config_filename = os.path.join('./%s/app.yaml' % project_name)
    config_file = open(config_filename, 'w')
    config_file.write(CONFIG_TEMPLATE % app_id)
    config_file.close()
    print 'Done!'
    print "To see it in action:"
    print "$ cd %s" % project_name
    print "$ python2.5 manage.py runserver"
    print "Visit http://localhost:8000 in your browser"


if __name__ == '__main__':
    execute_from_command_line()


