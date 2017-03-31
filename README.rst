=========================
wpy: web4mail cli client
=========================

Intro
============

A web4mail server accept web requests by mail and 
sends them back as an attachment.

In this case we use get@dameweb.info but any other could 
be easily supported.


Wpy is a command line tool, it gets easier to do 
Google searchs and request pages from the terminal.

Wpy build the request, connects to the smtp server
(using our config), and sends the mail to the w4mail server.

Wpy was built to use when you have no connection to the internet but a mail account.

Requirements
==============

Any OS with Python 2.5 or higher.

Install
===========

1. Get wpy: ::
   
     https://raw.github.com/xr09/wpy/master/w.py

2. Copy the file anywhere on your home folder, 
   here we assume is $HOME/apps/wpy
   
   .. code-block:: bash

     $ [ -d $HOME/.apps/wpy ] || mkdir -p $HOME/.apps/wpy
     $ mv w.py $HOME/.apps/wpy/
     $ chmod +x $HOME/.apps/wpy/w.py

3. Create config file:
   
   .. code-block:: bash
     
     $ touch $HOME/.wpy.cfg
     $ chmod 600 $HOME/.wpy.cfg

4. Edit ``.wpy.cfg`` (example):

   .. code-block:: ini

     [default]
     user=mail_user
     password=password
     mailserver=somemail.com

5. Create alias to use ``w.py``:

   .. code-block:: bash

     $ cat >> $HOME/.bashrc <<EOF
     alias wpy='python $HOME/apps/wpy/w.py'
     EOF

   Start a fresh terminal and try ``wpy``.

6. Try wpy:

   .. code-block:: bash
     
     $ wpy -h
     Options:
       -h, --help    show this help message and exit
       -g, --google  Google Search
       ...

Using wpy
==========

Simple google search:

   .. code-block:: bash
     
     $ wpy python
     Page requested: http://www.google.com/search?q=python

Request specific page:

   .. code-block:: bash
     
     $ wpy http://www.python.org/
     Page requested: http://www.python.org/

Twitter search:

   .. code-block:: bash
     
     $ wpy -t android
     Engine: Twitter
     Key Words: android

Wikipedia search:

   .. code-block:: bash
     
     $ wpy -w android
     Engine: Wikipedia (English)
     URL: http://en.wikipedia.org/wiki/Special:Search?search=android


In some minutes depending of server load you should receive a reply.
