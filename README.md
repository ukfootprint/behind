# behind

behind is a python3 recipe for setting up a Debian 10 server as a reverse proxy for a single virtual host using  a LetsEncrypt SSL secured Nginx instance. You can extend it to handle multiple virtual hosts as required.

First set up a basic install of Debian 10 with python 3, Git & SSH ( the latter optional - if you don't have console access) then clone this repository:

$  git clone https://github.com/ukfootprint/behind

Once cloned

$ cd behind

and run the setup script as the root user:

$ python3 setup.py

Fill in the required info as requested and when complete test your reverse proxied server / service from your remote browser.

Notes - 

  i) You'll need a public domain name with DNS routing HTTP(S) traffic to your server

  ii) You'll also need a valid email address when setting up your LetsEncrypt SSL certificate

  ii) There's no input validation so if you mess up then run the script again

  ii) It should work but there is no guarantee that this will work for you; use entirely at your own risk

Enjoy!
