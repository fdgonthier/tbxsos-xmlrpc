#!/usr/bin/env python2.5
# -*- mode: python; tab-width: 4; indent-tabs-mode: t; py-indent-offset: 4 -*-

###
### kps xmlrpc api server
###

# If you want this to work during development, do the following links.
#  /var/www/kpsapi/kpsapi.py -> $PWD/kpsapi.py
#  /var/www/kpsapi/kah.py -> $PWD/kah.py
#
# mod_setenv seems to do nothing at all.

# standard python stuff
import os, sys, xmlrpclib, re, \
       time, pickle, md5, base64, \
       glob, socket, stat

# tbxsosd-config daemon socket
if os.environ.has_key("TBXSOSD_CONFIGD_SOCKET"):
	TBXSOSD_CONFIGD_SOCKET=os.environ["TBXSOSD_CONFIGD_SOCKET"]
else:
	TBXSOSD_CONFIGD_SOCKET="/tmp/tbxsosd-configd-cmd"

from kah import *

# kpython
from klog import *
from krun import *

# kctllib
from kctllib.kdatabase import *

klog_set_name("kpsapi")

class KPSAPIException(Exception):
	pass

# basic session management

# called first - kinda sucks but...
def sessions_clean():
	files = glob.glob("/tmp/kpsapisess.*")
	for file in files:
		sid = file.split(".")[1]
		session = session_read(sid)
		ok = False
		if session != None:
			if session.has_key("start_stamp"):
				if session["start_stamp"] >= (time.time() - (600)): # valid for 10 minutes
					ok = True
		if ok != True:
			session_destroy(sid)		

# read session data, returns the session dictionnary
def session_read(sid):
	try:
		f = open("/tmp/kpsapisess."+str(sid), "rb")
		return pickle.load(f)
		f.close()
	except:
		return None

# writes session data
def session_write(sid, data):
	try:
		f = open("/tmp/kpsapisess."+str(sid), "wb")
		pickle.dump(data, f, 1)
		f.close()

		return True
	except:
		return False

# destroy session file
def session_destroy(sid):
	try:
		os.remove("/tmp/kpsapisess."+str(sid))
	except:
	# we're in cgi mode... we won't really see this.
		raise KCTLAPIException("Problem doing cleanups.")

# check if valid session id
def session_validate(sid):
	r = re.compile(r'^[a-zA-Z0-9+]+$')
	if r.match(sid) == None:
		raise KCTLAPIException("Invalid session ID.")

# check if loggued
def session_loggued(sid):
	session = session_read(sid)
	if session["loggued"] == True:
		return True
	raise KCTLAPIException("Invalid session.")

# generate a random string with characters: a-z, A-Z, 0-9, +
# I know...
def generate_random_string():
	m = md5.new()
	m.update(str(time.time()))
	r = re.compile(r'[^a-zA-Z0-9+]')
	return r.sub("", base64.encodestring(m.digest()))

# strip None values from value (they are not supported in xmlrpc: replace them with "")
# currently, we use: integers, strings and lists only
def xmlrpc_workaround(val):
	if type(val) == type(None) and val == None:
		val = "___NULL___"
	elif type(val) == type(True) and val == True:
		val = "___TRUE___"
	elif type(val) == type(False) and val == False:
		val = "___FALSE___"
	elif type(val) == type([]):
		# recurse through the list
		i=0
		while i < len(val):
			val[i] = xmlrpc_workaround(val[i])
			i = i + 1
	elif type(val) == type({}):
		# do not handle dict right now
		pass
		#for key in val.keys():
		#	val[key] = xmlrpc_workaround(val[key])
	return val

# methods available to the client
class KPSApi:
	def session_get_id(self):
		tries = 0
		while tries < 10:
			tries = tries + 1
			sid = generate_random_string()
			if session_read(sid) == None:
				session = {}
				session["loggued"] = False
				session["start_stamp"] = time.time()
				session_write(sid, session)
				return xmlrpc_workaround(sid)


	def session_log(self, sid, login, password):
		session_validate(sid)
		config = KIniConfig("/etc/teambox/tbxsos-xmlrpc/tbxsos-xmlrpc.ini")
		goodlogin = config.get("kpsapi", "login")
		goodpassword = config.get("kpsapi", "password")

		if goodlogin == None or goodpassword == None:
			raise KCTLAPIException("Application misconfigured.")

		if login == goodlogin and password == goodpassword:
			session = session_read(sid)
			session["loggued"] = True
			session_write(sid, session)
			return xmlrpc_workaround(True)

		raise KCTLAPIException("Invalid login or password.")

	def testint(self):
		return xmlrpc_workaround(123)

	def teststr(self):
		return xmlrpc_workaround("hello world!")

	def testarray(self):
		return xmlrpc_workaround([ "aa", None, "cc" ])

	def testdict(self):
		return xmlrpc_workaround({ "aa" : "bb", "vf" : None, "cc" : "fsf" })

	# needed only for tests...
	# is done with activations kaps
	#def addorg(self, sid, name):
	#	session_validate(sid)
	#	db_init()
	#	res = sdb_addorg(name)
	#	db_commit()
	#	return xmlrpc_workaround(res)

	def lsorg(self, sid):
		session_validate(sid)
		db_init()
		res = sdb_lsorg()
		db_commit()
		return xmlrpc_workaround(res)

	#def rmorg(self, sid, orgid):
	#	session_validate(sid)
	#	db_init()
	#	res = sdb_rmorg(orgid)
	#	db_commit()
	#	return xmlrpc_workaround(res)

	def setorgforwardto(self, sid, orgid, email):
		session_validate(sid)
		try:
			db_init()
			sdb_setorgforwardto(orgid, email)
			db_commit()
		except:
			raise KCTLAPIException("could not set organization forward_to")
		return xmlrpc_workaround(True)

	def addgroup(self, sid, org_id, group_name):
		session_validate(sid)
		db_init()
		group_id = kah_add_group(org_id, group_name)
		#prof_id = sdb_addgroup(org_id, group_name)
		#group_id = sdb_getprofilegroupid(prof_id)
		db_commit()
		return xmlrpc_workaround(group_id)

	def lsgroups(self, sid):
		session_validate(sid)
		db_init()
		res = sdb_lsprofiles()
		db_commit()
		return xmlrpc_workaround(res)

	def rmgroup(self, sid, group_id):
		# no check for profile being a group - just hide the "profiles" notion for this api
		session_validate(sid)
		db_init()
		prof_id = sdb_getgroupprofileid(group_id)
		res = sdb_rmprofile(prof_id)
		db_commit()
		return xmlrpc_workaround(res)

	def addldapgroup(self, sid, group_id, group_dn):
		session_validate(sid)
		db_init()
		res = sdb_addldapgroup(group_id, group_dn)
		db_commit()
		return xmlrpc_workaround(res)

	def getprofilegroupid(self, sid, prof_id):
		session_validate(sid)
		db_init()
		res = sdb_getprofilegroupid(prof_id)
		db_commit()
		return xmlrpc_workaround(res)

	def lsldapgroups(self, sid, group_id):
		session_validate(sid)
		db_init()
		res = sdb_lsldapgroups(group_id)
		db_commit()
		return xmlrpc_workaround(res)
	
	def rmldapgroup(self, sid, ldap_group_id):
		session_validate(sid)
		db_init()
		res = sdb_rmldapgroup(ldap_group_id)
		db_commit()
		return xmlrpc_workaround(res)

	def get_new_id_act(self, sid):
		session_validate(sid)
		db_init()
		res = kah_get_new_id_act()
		return xmlrpc_workaround(res)

	def get_kar_act(self, sid, id, admin_name, admin_email, country, state, location, org, org_unit, domain, email):
		session_validate(sid)
		db_init()
		res = kah_get_kar_act(id, admin_name, admin_email, country, state, location, org, org_unit, domain, email)
		return xmlrpc_workaround(res)

	def set_kap_act(self, sid, id, base64_kap):
		kap = base64.standard_b64decode(base64_kap)
		session_validate(sid)
		db_init()
		res = kah_set_kap_act(id, kap)
		return xmlrpc_workaround(res)

    def list_logs(self, sid):
        return xmlrpc_workaround(os.listdir("/var/log/teambox"))

	def get_log(self, sid, log_file_name):
		session_validate(sid)
		try:
            log_file_path = "/var/log/teambox/%s" % log_file_name
            log_file_stat = os.stat(log_file_path)
            if stat.S_ISREG(log_file_stat[stat.ST_MODE]):
                f = open(log_file_path)
                res = f.read()
                f.close()
                return xmlrpc_workaround(res)
		except Exception, e:
			err(str(e))
			return xmlrpc_workaround(None)

	def reboot(self, sid):
		session_validate(sid)
		try:
			client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			client.connect(TBXSOSD_CONFIGD_SOCKET)
			client.send("reboot\n")
			res = ""
			while 1:
				data = client.recv(1024)
				if not data: break
				res = res + data
			client.close()
			if res == "ok\n":
				return xmlrpc_workaround(True)
		except Exception, e:
			err(str(e))
			raise

		return xmlrpc_workaround(False)

	def free_login_seat(self, sid, org_id, username):
		session_validate(sid)
		db_init()
		res = sdb_freeloginseat(org_id, username)
		db_commit()
		return xmlrpc_workaround(res)

	def set_seats_allocation(self, sid, parent_org_id, org_id, number):
		session_validate(sid)
		#db_init()
		#res = sdb_setseatsallocation(parent_org_id, org_id, number)
		#db_commit()
		cmd = ["kctl", "setseatsallocation", str(parent_org_id), str(org_id), str(number) ]
		proc = KPopen("", cmd) # "" is data sent to stdin
		if proc.return_code == 0:
			return xmlrpc_workaround(True)
		raise KCTLAPIException(proc.stderr)

	def ls_seats_org(self, sid, org_id):
		session_validate(sid)
		db_init()
		res = sdb_lsseatsorg(org_id)
		db_commit()
		return xmlrpc_workaround(res)


def main():
	sessions_clean()

	from SimpleXMLRPCServer import CGIXMLRPCRequestHandler

	# do commit changes
	kparams_set("commit", True)

	# enable redirection of all output to syslog
	do_logredirect()

	server = CGIXMLRPCRequestHandler() #allow_none=1)
	server.register_introspection_functions()
	server.register_instance(KPSApi())

	server.handle_request()

if __name__ == "__main__":
	main()



