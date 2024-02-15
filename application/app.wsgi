import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/home/project/csc-648-02-spring24-team05/application")

from app import app as application
application.secret_key = 'testing'