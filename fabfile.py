#!/usr/bin/env python
import sys,os,datetime
sys.path.insert(0,os.path.dirname(__file__))
from fabric.api import *
from toughtester import __version__

currtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def push():
    message = raw_input("commit msg:")
    local("git add .")
    try:
        local("git commit -m \'%s - %s: %s\'"%(__version__, currtime, message))
    except:
        print 'no commit'
    local("git push origin master")
    

def tag():
    local("git tag -a v%s -m 'version %s'"%(__version__,__version__))
    local("git push origin v%s:v%s"%(__version__,__version__))

def worker():
    local("pypy toughctl --worker -c test.json")


def admin():
    local("pypy toughctl --admin -c test.json")


def initdb():
    local("pypy toughctl --initdb -c test.json")

def uplib():
    local("pypy -m pip install https://github.com/talkincode/toughlib/archive/master.zip --upgrade --no-deps")

def uplib2():
    local("pypy -m pip install https://github.com/talkincode/txportal/archive/master.zip --upgrade --no-deps")

def uplib3():
    local("pypy -m pip install https://github.com/talkincode/txradius/archive/master.zip --upgrade --no-deps")