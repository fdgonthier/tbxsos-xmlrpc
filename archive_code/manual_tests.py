#!/usr/bin/env python
# -*- mode: python; python-indent-tabs-mode: t; python-indent-level: 4; tab-width: 4 -*-

###
### manual tests for xmlrpc api
###

import sys
import xmlrpclib
import base64

server_url = "http://localhost/kpsapi/kpsapi.py"
server_login = "admin"
server_password = "admin"


sid = None
server = None

def xmlrpc_correct(val):
	if val == "___NULL___":
		val = None
	elif val == "___TRUE___":
		val = True
	elif val == "___FALSE___":
		val = False
	elif type(val) == type([]):
		# recurse through the list
		i=0
		while i < len(val):
			val[i] = xmlrpc_correct(val[i])
			i = i + 1
	elif type(val) == type({}):
		# do not handle dict right now
		pass
		#for key in val.keys():
		#   val[key] = xmlrpc_correct(val[key])
	return val

def test_orgs():
	#neworgid = xmlrpc_correct(server.addorg(sid, "lameorg"))
	#print "Added new organization: " + str(neworgid)
	#print "lsorg: " + str(xmlrpc_correct(server.lsorg(sid)))
	#server.setorgforwardto(sid, neworgid, "lalala@lilili")
	#print "Changed the forward_to to 'lalala@lilili'"
	#print "lsorg: " + str(xmlrpc_correct(server.lsorg(sid)))
	#server.setorgforwardto(sid, neworgid, "")
	#print "Changed the forward_to to ''"
	print "lsorg: " + str(xmlrpc_correct(server.lsorg(sid)))
	#print "rmorg " + str(neworgid)
	#server.rmorg(sid, neworgid)
	#print "lsorg: " + str(xmlrpc_correct(server.lsorg(sid)))
	#xmlrpc_correct(server.rmorg(sid, 999999))

def test_profiles():
	# test profiles
	print "ADD ORG:"
	neworgid = xmlrpc_correct(server.addorg(sid, "some org"))
	print "ORG %d added" % neworgid

	print "ADD GROUP:"
	newgroupid = xmlrpc_correct(server.addgroup(sid, neworgid, "some group"))
	print "GROUP %d added" % newgroupid

	print "GROUPS LIST:"
	print xmlrpc_correct(server.lsgroups(sid))

	print "ADDING LDAP GROUP:"
	newldapgroupid = xmlrpc_correct(server.addldapgroup(sid, newgroupid, "dc=lll,dc=lll"))
	print "LDAP GROUP: %s" % str(newldapgroupid)

	print "ADDING LDAP GROUP:"
	newldapgroupid = xmlrpc_correct(server.addldapgroup(sid, newgroupid, "dc=lll,dc=llasdfsl"))
	print "LDAP GROUP: %s" % str(newldapgroupid)

	print "LDAP GROUPS LIST:"
	print xmlrpc_correct(server.lsldapgroups(sid, newgroupid))

	print "RM LDAP GROUP:"
	print xmlrpc_correct(server.rmldapgroup(sid, newldapgroupid))

	print "LDAP GROUPS LIST:"
	print xmlrpc_correct(server.lsldapgroups(sid, newgroupid))

	print "RM GROUP:"
	print xmlrpc_correct(server.rmgroup(sid, newgroupid))

	print "LISTE PROFILES:"
	print xmlrpc_correct(server.lsgroups(sid))

	print "LISTE ORGS:"
	print xmlrpc_correct(server.lsorg(sid))

	print "RM ORG:"
	print xmlrpc_correct(server.rmorg(sid, neworgid))

	print "LISTE ORGS:"
	print xmlrpc_correct(server.lsorg(sid))


def test_kar_act():
	id = xmlrpc_correct(server.get_new_id_act(sid))
	if id == False:
		raise "Could not get a new activation id... don't know why exactly"
	print "ID: " + str(id) + "\n"
	kar = xmlrpc_correct(server.get_kar_act(sid, id, \
		"admin_name", "admin_email", "country", "state", "location", "org", "org_unit", "domain", "email"))
	f = open("/tmp/kar.bin", "w")
	f.write(kar)
	f.close()
	print "KAR: " + str(kar) + "\n"


def test_kap_act():
	id = "0004"
	kap_file = "/tmp/kap.bin"
	f = open(kap_file, "r")
	kap = f.read()
	f.close()
	#print kap
	b64kap = base64.standard_b64encode(kap)
	#print b64kap
	status = xmlrpc_correct(server.set_kap_act(sid, id, b64kap))
	print "STATUS: " + str(status)


def test_logs():
	print "LOGS: \n"
	print xmlrpc_correct(server.get_logs(sid))


def test_backup():
	backup = xmlrpc_correct(server.backup(sid))
	if backup == None:
		raise("Failed to backup for an unknown reason... check the logs.")
	print "Backup len: " + str(len(backup))
	res = xmlrpc_correct(server.restore(sid, backup))
	if res == None:
		raise("Failed to restore for an unknown reason... check the logs.")

	print "RESTORE: " + str(res)


def test_reboot():
	## test reboot
	print xmlrpc_correct(server.reboot(sid))


def test_seats():
	## test seats functions
	parent_org_id = 2
	org_id = 9
	username = 'lalala'
	number = 55
	try:
		print "free login seat:"
		print xmlrpc_correct(server.free_login_seat(sid, org_id, username))
	except Exception, ex:
		print str(ex)
	try:
		xmlrpc_correct(server.set_seats_allocation(sid, parent_org_id, org_id, number))
	except Exception, ex:
		print str(ex)
	try:
		print xmlrpc_correct(server.ls_seats_org(sid, org_id))
	except Exception, ex:
		print str(ex)


def connect():
	global server
	global sid

	server = xmlrpclib.ServerProxy(server_url) #, allow_none=1)
	#print xmlrpc_correct(server.system.listMethods())

	print
	sid = xmlrpc_correct(server.session_get_id())
	print "Session ID: " + sid
	if xmlrpc_correct(server.session_log(sid, server_login, server_password)):
		print "Loggued successfully."
		return True

	print "Could not log."
	return False


def main():
	if connect():
		#funcs = [ test_reboot ]
		funcs = [ test_orgs, test_profiles, test_kar_act, test_logs, test_backup, test_seats ]
		#funcs = [ test_kar_act ]
		#funcs = [ test_kap_act ]
		i=-1
		count=len(funcs)
		while i < (count-1):
			i += 1
			func = funcs[i]
			print
			print
			print
			print "function " + str(func) + ":"
			print

			try:
				func()
			except Exception, ex:
				print "FAILED: '" + str(ex) + "'"

			print
			if i < (count - 1):
				print "Press enter for the next set of tests..."
				sys.stdin.readline()


main()


