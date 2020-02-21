# hidden

This is a python3 recipe for setting up a Debian 10 server as a reverse proxy for a single virtual host using  a LetsEncrypt SSL secured Nginx instance. User could extend it to handle multiple virtual hosts as necessary.

First set up a basic install of Debian 10 with python 3, Git & SSH (optional; if you don't have console access) then clone this repository:

$  git clone https://github.com/ukfootprint/hidden

Once cloned

$ cd hidden

and run the setup script as the root user:

$ python3 setup.py

Fill in the required info when prompted and when complete these connection to your reverse proxied server / service.

Notes - 

i) There's no input validation so if you mess up then run the script again.
ii) It should work but there is no guarantee that this will work for you; use at your own risk 

Enjoy!
