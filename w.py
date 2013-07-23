#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from sys import stderr, exit

from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate
from optparse import OptionParser
from ConfigParser import SafeConfigParser

DEFAULT_CONFIG_FILE = os.path.expanduser('~/.wpy.cfg')
VERSION = "0.3.2"

class bcolors:
    HEADER = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def parseOpts():
    parser = OptionParser()
    parser.add_option("-g", "--google", action="store_const", const=0,
        dest="engine", help="Search in Google")
    parser.add_option("-t", "--twitter", action="store_const", const=1,
        dest="engine", help="Search in Twitter microblogging service")
    parser.add_option("-b", "--bing", action="store_const", const=2,
        dest="engine", help="Search using Bing")
    parser.add_option("-u", "--url", action="store_const", const=3,
        dest="engine", help="Fetch the page in this URL")
    parser.add_option("-p", "--pack", action="store_const", const=4,
        dest="engine", help="Fetch the compressed page (includes CSS and images)")
    parser.add_option("-w", "--we", action="store_const", const=5,
        dest="engine", help="Search using Wikipedia (English version)")
    parser.add_option("-s", "--ws", action="store_const", const=6,
        dest="engine", help="Search using Wikipedia (Spanish version)")

    return parser.parse_args()


class WosRequest(object):
    '''
    WOS based request
    '''
    def __init__(self, args):
        self.server = 'get@dameweb.info'
        self.prefix = ""
        self.args = args
        self.title = "Simple Request"
    
    def content(self):
        '''
        Returns the subject of the mail request
        '''
        return (self.prefix + " " + self.params())
    
    def params(self):
        '''
        Returns the request params, generally a concatenation
        of the command line args
        '''
        return " ".join(self.args)
    
    def showURL(self):
        '''
        Prints the content in a nice color
        '''
        print bcolors.HEADER + "URL: " + bcolors.ENDC + bcolors.OKGREEN + self.content() + bcolors.ENDC
    
    def showEngine(self):
        '''
        Prints the used engine in the current request
        '''
        print bcolors.HEADER + "Engine: " + bcolors.ENDC + bcolors.OKGREEN + self.title + bcolors.ENDC
    
    def showKeyWords(self):
        '''
        Prints the params in a nice color
        '''
        print bcolors.HEADER + "Key Words: " + bcolors.ENDC + bcolors.OKGREEN + self.params() + bcolors.ENDC
    
    def showInfo(self):
        '''
        Prints the engine and keywords in a nice color
        '''
        self.showEngine()
        self.showKeyWords()
    
    def mail(self, ident):
        '''
        Returns the mail object to send
        '''
        msg = MIMEMultipart()
        msg['From'] = ident
        msg['To'] = self.server 
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = self.content()
        return msg


class Google(WosRequest):
    '''
    Google search
    '''
    def __init__(self, args):
        super(Google, self).__init__(args)
        self.prefix = "google:"
        self.title = "Google"


class Twitter(WosRequest):
    '''
    Twitter search
    '''
    def __init__(self, args):
        super(Twitter, self).__init__(args)
        self.prefix = "twitter:"
        self.title = "Twitter"


class Bing(WosRequest):
    '''
    Bing search
    '''
    def __init__(self, args):
        super(Bing, self).__init__(args)
        self.prefix = "bing:"
        self.title = "Bing"


class HTTP(WosRequest):
    '''
    HTTP Basic Request
    '''
    def __init__(self, args):
        super(HTTP, self).__init__(args)
        self.title = "HTTP Request"
    
    def showInfo(self):
        self.showEngine()
        self.showURL()
    
    def content(self):
        if self.args[0].startswith('http://www.google.com/url'):
            start = self.args[0].find("http", 25)
            end =  self.args[0].find("&", start)
            return "".join(self.args[0][start:end]).strip()
        elif not self.args[0].startswith('http://'):
            raise Exception("You must specify at least one word to search")
        else:
            return "".join(self.args).strip()

class Pack(HTTP):
    '''
    HTTP (pack mode) request
    '''
    def __init__(self, args):
        super(HTTP, self).__init__(args)
        self.title = "HTTP (Pack Mode)"
        self.server = "pack@dameweb.info"

class Wikipedia(HTTP):
    '''
    Wikipedia search
    '''
    def __init__(self, args):
        super(Wikipedia, self).__init__(args)
        self.title = "Wikipedia (English)"
        self.prefix = "http://en.wikipedia.org/wiki/Special:Search?search="

    def params(self):
        return "+".join(self.args)

    def content(self):
        return self.prefix + self.params()

class WikipediaSpanish(Wikipedia):
    def __init__(self, args):
        super(WikipediaSpanish, self).__init__(args)
        self.title = "Wikipedia (Spanish)"
        self.prefix = "http://es.wikipedia.org/wiki/Special:Search?search="

class RequestFactory(object):
    @staticmethod
    def getRequest(engine=0, args=None):
        if not engine:
            if args[0].startswith("http://"):
                return HTTP(args)
            return Google(args)
	engines = {
	    1: Twitter,
	    2: Bing,
	    3: HTTP,
	    4: Pack,
	    5: Wikipedia,
	    6: WikipediaSpanish
	}
	return engines[engine](args)

class Client(object):
    def __init__(self):
        self.ident = ""
        self.user = ""
        self.password  = ""
        self.mailserver = ""
        try:
            self.parseConfig(DEFAULT_CONFIG_FILE)
            (self.options, self.args) = parseOpts()
            if not self.args: raise Exception("You must specify at least one word to search")
        except Exception, e:
            print >>stderr, bcolors.WARNING + "%s" % e + bcolors.ENDC
            exit(1)
    
    def parseConfig(self, config_file):
        parser = SafeConfigParser()
        try:
            parser.read(config_file)
            self.user = parser.get('default', 'user')
            self.ident = "%s <%s>" % (self.user.split("@")[0], self.user)
            self.password = parser.get('default', 'password')
            self.mailserver = parser.get('default', 'mailserver')
        except Exception, e:
            print >>stderr, bcolors.WARNING + "Please check the configuration file.\n%s" % e + bcolors.ENDC
            exit(1)
        return True
    
    def requestUrl(self):
        eng = self.options.engine or 0
        request = RequestFactory.getRequest(engine=eng,args=self.args)
        self.__sendMail(request)
        request.showInfo()
    
    def __sendMail(self, request):
        try:
            smtp = SMTP(self.mailserver)
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            if self.user:
                smtp.login(self.user, self.password)
            msg = request.mail(self.ident)
            smtp.sendmail(self.ident, request.server, msg.as_string())
            smtp.close()
        except Exception, e:
            print >>stderr, bcolors.FAIL + "Error connecting to mail server,\
             please check your settings\n%s" % e + bcolors.ENDC
            exit(1)
        return None

if __name__ == '__main__':
    client = Client()
    client.requestUrl()

