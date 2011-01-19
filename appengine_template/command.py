# -*- coding: utf-8 -*-
import os
import sys

def execute_from_command_line():
    args = sys.argv[1:]
    if len(args) < 1:
        print 'Usage: startappengineproject [app_id]'
        sys.exit(-1)
    app_id = args[0]
    print "Building new app: %s" % app_id
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # Clear out any preexisting project
    try:
        os.mkdir('project')
    except OSError, e:
        print "Sorry. Project directory already exists."
        exit()
    # Copy in the template
    os.system('cp -R %s ./project' % current_dir)
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
- url: /.*
  script: main.py

- url: /remote_api 
  script: $PYTHON_LIB/google/appengine/ext/remote_api/handler.py 
  login: admin

- url: /media
  static_dir: media
"""

if __name__ == '__main__':
    execute_from_command_line()


