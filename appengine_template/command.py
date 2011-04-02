# -*- coding: utf-8 -*-
import re
import os
import sys

ALLOWED_APPIDS = re.compile('^(?:[a-z\d\-]{1,100}\~)?(?:(?!\-)[a-z\d\-\.]{1,100}:)?(?!-)[a-z\d\-]{1,100}$')

def execute_from_command_line():
    """
    A command-line utility that will create a virgin Google App Engine
    project enabled to use Django.
    
    The first argument is expected to contain the app_id the creator plans
    to register with Google.
    """
    # Parse the command line arguments
    args = sys.argv[1:]
    if len(args) < 1:
        print 'Usage: startappengineproject [app_id]'
        sys.exit(-1)
    app_id = args[0]
    
    # Validate the provided app_id
    if not ALLOWED_APPIDS.match(app_id):
        print "The provided app_id, %s, will not be accepted by Google." % app_id
        print "It probably has some underscores or other such things they do not allow."
        exit()
    
    print "Building new app: %s" % app_id
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir[-1] != '/':
        current_dir += '/'
    
    # Clear out any preexisting project
    if os.path.isdir("project"):
        print "Sorry. Project directory already exists."
        exit()
    
    # Copy in the template
    cp = 'cp -R %s ./project' % current_dir
    print cp
    os.system(cp)
    
    # Move the SDK to a dot folder
    os.system('mv ./project/google_appengine/ ./project/.google_appengine/')
    
    # Load the app_id into the config file
    config_filename = os.path.join('./project/app.yaml')
    config_file = open(config_filename, 'w')
    config_file.write(config_template % app_id)
    config_file.close()
    print 'Done!'
    print "To see it in action:"
    print "$ cd project"
    print "$ python2.5 manage.py runserver"
    print "Visit http://localhost:8000 in your browser"

config_template = """application: %s
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

if __name__ == '__main__':
    execute_from_command_line()


