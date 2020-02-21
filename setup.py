# Adapted from https://github.com/dhicks6345789/remote-gateway

#!/usr/bin/python3

import os
import sys
import shutil

# Parse any options set by the user on the command line.
validBooleanOptions = []
validValueOptions = ["-serverNAME", "-serverDOMAIN", "-serverIP", "-serverNETMASK",  "-serverGATEWAY", "-serverDNS1", "-serverDNS2", "-targetHostIP", "-targetHostPort"]

userOptions = {}
optionCount = 1
while optionCount < len(sys.argv):
    if sys.argv[optionCount] in validBooleanOptions:
        userOptions[sys.argv[optionCount]] = True
    elif sys.argv[optionCount] in validValueOptions:
        userOptions[sys.argv[optionCount]] = sys.argv[optionCount+1]
        optionCount = optionCount + 1
    optionCount = optionCount + 1

def runIfPathMissing(thePath, theCommand):
    if not os.path.exists(thePath):
        print("Running: " + theCommand)
        os.system(theCommand)
        
def copyfile(src, dest, mode=None):
    srcStat = os.stat(src)
    if (not os.path.exists(dest)) or (not str(srcStat.st_mtime) == str(os.stat(dest).st_mtime)):
        print("Copying file " + src + " to " + dest)
        shutil.copyfile(src, dest)
        os.utime(dest, (srcStat.st_atime, srcStat.st_mtime))
        if not mode == None:
            os.system("chmod " + mode + " " + dest)
        return(1)
    return(0)

def getUserOption(optionName, theMessage):
    if not optionName in userOptions.keys():
        userOptions[optionName] = input(theMessage + ": ")
    return(userOptions[optionName])

def readFile(theFilename):
    fileDataHandle = open(theFilename, "r")
    fileData = fileDataHandle.read()
    fileDataHandle.close()
    return(fileData)
    
def writeFile(theFilename, theFileData):
    fileDataHandle = open(theFilename, "w")
    if isinstance(theFileData, list):
        fileDataHandle.write("\n".join(theFileData))
    else:
        fileDataHandle.write(theFileData)
    fileDataHandle.close()
    
def replaceVariables(theFile, theKeyValues):
    fileData = readFile(theFile)
    for keyValue in theKeyValues.keys():
        fileData = fileData.replace("<<" + keyValue + ">>", theKeyValues[keyValue])
    writeFile(theFile, fileData)    

print("Just checking for some necessary packages...")
# Make sure dos2unix (line-end conversion utility) is installed.
runIfPathMissing("/usr/bin/dos2unix", "apt-get install -y dos2unix")

# Make sure Pip3 (Python 3 package manager) is installed
runIfPathMissing("/usr/bin/pip3", "apt-get install -y python3-pip")

# Make sure resolvconf is installed - manages conflicts writing to resolv.conf
runIfPathMissing("/etc/resolvconf.conf", "apt-get install -y resolvconf")

# Figure out what version of Python3 we have installed.
#pythonVersion = os.popen("ls /usr/local/lib | grep python3").read().strip()

# First, get some host information from the user
print("Installing...")
getUserOption("-serverNAME", "Please enter this server's name (e.g. myserver)")
getUserOption("-serverDOMAIN", "Please enter this server's routable domain name ( e.g. mydomain.com)")
getUserOption("-serverIP", "Please enter this server's static IPv4 (e.g. 192.168.0.10)")

# Next copy over hosts file and set the hostname
print("Configuring...")
os.system("cp hosts /etc/hosts")
#os.system("chown root:root /etc/hosts")
#os.system("chmod u+x /etc/hosts")
os.system("hostnamectl set-hostname" + " " + userOptions["-serverNAME"] + "." + userOptions["-serverDOMAIN"])
replaceVariables("/etc/hosts", {"SERVERNAME":userOptions["-serverNAME"]})
replaceVariables("/etc/hosts", {"SERVERDOMAIN":userOptions["-serverDOMAIN"]})
replaceVariables("/etc/hosts", {"SERVERIP":userOptions["-serverIP"]})
# Check hosts configuration 
#os.system("hostnamectl > /dev/null 2>&1")
#os.system("sleep 3")

#Then get some networking info from the user
print("Installing...")
getUserOption("-serverNetmask", "Please enter the server's subnet mask (e.g. 255.255.254.0)")
#getUserOption("-serverBoadcast", "Please enter the network broadcast address (e.g. 192.168.1.255)")
getUserOption("-serverGateway", "Please enter this server's gateway  (e.g. 192.168.1.254)")
getUserOption("-serverDNS1", "Please enter this server's primary DNS server (e.g. 192.168.1.1)")
getUserOption("-serverDNS2", "Please enter this server's secondary DNS server (e.g. 192.168.1.2). Press RETURN if none")

# Next copy over network config file and set a static IP
print("Configuring...")
os.system("systemctl stop networking")
os.system("cp interfaces /etc/network/interfaces")
#os.system("chown root:root /etc/network/interfaces")
#os.system("chmod u+x /etc/network/interfaces")
replaceVariables("/etc/network/interfaces", {"SERVERIP":userOptions["-serverIP"]})
replaceVariables("/etc/network/interfaces", {"NETMASK":userOptions["-serverNetmask"]})
replaceVariables("/etc/network/interfaces", {"GATEWAY":userOptions["-serverGateway"]})
replaceVariables("/etc/network/interfaces", {"DNS1":userOptions["-serverDNS1"]})
replaceVariables("/etc/network/interfaces", {"DNS2":userOptions["-serverDNS2"]})
os.system("systemctl restart networking")
os.system("sleep 3") 

#Finally get details of the reverse proxied host from the user
getUserOption("-targetHostIP", "Please enter the target host IPv4 for Nginx to reverse proxy (e.g. 192.168.1.12)")
getUserOption("-targetHostPort", "Please enter the target host port # for Nginx to reverse proxy (e.g. 8080)")

# Make sure the Nginx web/proxy server is installed (used for reverse proxy of incoming requests to target host and provide SSL)...
runIfPathMissing("/usr/share/doc/nginx", "apt-get install -y nginx")
# ...with support for Let's Encrypt. See here:
# https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-debian-10
# Also, see later  crontab section herein for monthly certbot renew / backup process.
runIfPathMissing("/usr/lib/python3/dist-packages/certbot", "apt-get install -y python3-acme python3-certbot-nginx python3-mock python3-openssl python3-pkg-resources python3-pyparsing python3-zope.interface")

# Make sure UFW is installed (easy to use front end to Debian firewall).
runIfPathMissing("/usr/share/doc/ufw", "apt-get install -y ufw")

# Set up firewall rules - allow SSH, Nginx Full (HTTP and HTTPS) ingress
os.system("ufw allow OpenSSH > /dev/null 2>&1")
os.system("ufw allow 'Nginx Full' > /dev/null 2>&1")
os.system("echo y | ufw enable > /dev/null 2>&1")

#Finally get details of host to reverse proxy 
print("Configuring...")
getUserOption("-targetHostIP", "Please enter the host (IPv4) that Nginx will reverse proxy to (e.g. 192.168.1.12):")
getUserOption("-targetHostPort", "Please enter the port # that Nginx will reverse proxy to (e.g. 8080):")

# Copy over the optimised Nginx config files and insert user supplied values 
os.system("cp nginx.conf /etc/nginx/nginx.conf")
#os.system("chown root:root /etc/nginx/nginx.conf")
#os.system("chmod u+x /etc/nginx/nginx.conf")
os.system("cp sites-available-template /etc/nginx/sites-available/" + userOptions["-serverNAME"] + "." + userOptions["-serverDOMAIN"])
replaceVariables("/etc/nginx/sites-available/" + userOptions["-serverNAME"] + "." + userOptions["-serverDOMAIN"], {"SERVERNAME":userOptions["-serverNAME"]})
replaceVariables("/etc/nginx/sites-available/" + userOptions["-serverNAME"] + "." + userOptions["-serverDOMAIN"], {"SERVERDOMAIN":userOptions["-serverDOMAIN"]})
replaceVariables("/etc/nginx/sites-available/" + userOptions["-serverNAME"] + "." + userOptions["-serverDOMAIN"], {"HOSTIP":userOptions["-targetHostIP"]})
replaceVariables("/etc/nginx/sites-available/" + userOptions["-serverNAME"] + "." + userOptions["-serverDOMAIN"], {"PORT":userOptions["-targetHostPort"]})
#os.system("chown root:root /etc/nginx/sites-available/" + userOptions["-serverNAME"] + "." + userOptions["-serverDOMAIN"])
#os.system("chmod u+x /etc/nginx/sites-available/" + userOptions["-serverNAME"] + "." + userOptions["-serverDOMAIN"])
os.system("ln -s /etc/nginx/sites-available/" + userOptions["-serverNAME"] + "." + userOptions["-serverDOMAIN"] + " /etc/nginx/sites-enabled/")

# Set up SSL certificate
# If site already exists do "certbot certonly --nginx"...
runIfPathMissing("/etc/letsencrypt/" + userOptions["-serverNAME"] + "." + userOptions["-serverDOMAIN"], "certbot --nginx -d " + userOptions["-serverNAME"] + "." + userOptions["-serverDOMAIN"])
# put in a check to not run this if the above has just run
os.system("certbot certonly --nginx")
os.system("systemctl reload nginx")

# Restart Nginx
print("Restarting Nginx with new configuarion...")
os.system("systemctl restart nginx")

# Set up Cron to run the certbot renew
copyfile("crontab", "/var/spool/cron/crontabs/root", mode="0600")
os.system("dos2unix monthlyCronjob.sh > /dev/null 2>&1")

# Restart Cron
os.system("/etc/init.d/cron restart")
