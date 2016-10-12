import json
import time
import nose.plugins.attrib
import unittest2 as unittest
import requests
import argparse
import subprocess
from subprocess import PIPE
import os
#sample command line
#CR_USERNAME=amishra+prod1@apteligent.com CR_PASSWORD=Test_789 CR_CLIENT_ID=4IfWHRGz1DE357nnXRGNNs1QtbfESDxc NR_ACCOUNT_ID=59322 NR_INSERT_KEY=_3MI0XKVl7SWYfIpLyqTUA5jGAy2wHdI ./new_relic_connector.py upload 519d53101386202089000007


#command line used in the test 
#python NewRelic_Test.py  -u amishra+prod1@apteligent.com -p Test_789 -c 4IfWHRGz1DE357nnXRGNNs1QtbfESDxc -n 59322 -k _3MI0XKVl7SWYfIpLyqTUA5jGAy2wHdI -a 519d5310138620208900000

parser = argparse.ArgumentParser(description='Script to kick off the New Relic Automation')
parser.add_argument('-u',"--username",type=str, help='username',required=True,default="amishra+prod1@apteligent.com")
parser.add_argument('-p',"--password", type=str, help='password',required=True, default='Test_789')
def validate_new_relic_output():
  print "Validating output"

parser.add_argument('-c',"--clientid",type=str,help='client_id',required=True,default='4IfWHRGz1DE357nnXRGNNs1QtbfESDxc')
parser.add_argument('-n',"--NR_Account_id",type=str,help='NR_Account_id',required=True,default='59322')
parser.add_argument('-k',"--NR_insert_key",type=str,help='NR_insert_key',required=True,default='_3MI0XKVl7SWYfIpLyqTUA5jGAy2wHdI')
parser.add_argument('-a',"--app_id",type=str,help="app_id",required=True, default="519d53101386202089000007")


args = parser.parse_args()
username=args.username
password=args.password
clientid=args.clientid
NR_Account_id=args.NR_Account_id
NR_insert_key=args.NR_insert_key
app_id=args.app_id


def run_new_relic_automation():
  print "Running new Relic Automation in Production"
  param_list=[args.username, args.password,args.clientid,args.NR_Account_id,args.NR_insert_key,args.app_id ]
  cmd="CR_USERNAME={0} CR_PASSWORD={1} CR_CLIENT_ID={2} NR_ACCOUNT_ID={3} NR_INSERT_KEY={4} ./new_relic_connector.py upload {5}".format(*param_list)
  print "Executing command line" 
  print cmd
  P=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  out,err=P.communicate("all went well")
  print out  
  if  "500" or "404" in err:
       print "Test failed"
if __name__ == '__main__':
  run_new_relic_automation()
