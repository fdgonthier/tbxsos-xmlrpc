#!/usr/bin/env python
# -*- mode: python; python-indent-tabs-mode: nil; python-indent-level: 4; tab-width: 4 -*-

###
### python wrapper for calling kpsapihelper, which is part of tbxsosd-config right now
###

### sucks... 

import sys
import os
import tempfile
import subprocess
import uuid

# kpython
from kout import *

### create new identity, return id
def kah_get_new_id_act():
    try:
        tf = TmpWorkFile()
        kah_proc(["kpsapihelper", "get_new_id_act", tf.name])
        id = tf.read()
        tf.close()
        return id
    except Exception, e:
        err(str(e))
        return False


### get kar
def kah_get_kar_act(id, admin_name, admin_email, country, state, location, org, org_unit, domain, email):
    s = ""
    s = s + "[main]\n"
    s = s + "admin_name=%s\n" % ( str(admin_name) )
    s = s + "admin_email=%s\n" % ( str(admin_email) )
    s = s + "[csr]\n"
    s = s + "country=%s\n" % ( str(country) )
    s = s + "state=%s\n" % ( str(state) )
    s = s + "location=%s\n" % ( str(location) )
    s = s + "org=%s\n" % ( str(org) )
    s = s + "org_unit=%s\n" % ( str(org_unit) )
    s = s + "domain=%s\n" % ( str(domain) )
    s = s + "email=%s\n" % ( str(email) )

    try:
        tf_config = TmpWorkFile()
        tf_kar = TmpWorkFile()
        tf_config.write(s)
        tf_config.flush()

        kah_proc(["kpsapihelper", "get_kar_act", id, tf_config.name, tf_kar.name])
        kar = tf_kar.read()
        tf_config.close()
        tf_kar.close()
        return kar
    except Exception, e:
        err(str(e))
        return False


### activate
def kah_set_kap_act(id, kap):
    try:
        tf = TmpWorkFile()
        tf.write(kap)
        tf.flush()
        kah_proc(["kpsapihelper", "set_kap_act", id, tf.name])
        return True
    except Exception, e:
        err(str(e))
        return False


### add group
def kah_add_group(org_id, group_name):
    try:
        tf = TmpWorkFile()
        kah_proc(["kpsapihelper", "add_group", str(org_id), group_name, tf.name])
        group_id = int(tf.read())
        tf.close()
        return group_id
    except Exception, e:
        err(str(e))
        return False


### get a backup of database and kps config
def kah_backup():
    try:
        tf = TmpWorkFile()
        kah_proc(["kpsapihelper", "backup", tf.name])
        backup = tf.read()
        tf.close()
        return backup
    except Exception, e:
        err(str(e))
        return None

# yeah..
# had problems using tempfile.NamedTemporaryFile() when trying to read a file after it has been written by another proc
# IS NOT A COMPATIBLE FILE OBJECT
# you must call close() if you want the file to be removed!
class TmpWorkFile:
    def __init__(self):
        self.name = "/tmp/kah_" + str(uuid.uuid4())

    

    def read(self):
        try:
            f = open(self.name, "r")
            data = f.read()
            f.close()
            return data
        except:
            return None

    def write(self, data):
        try:
            f = open(self.name, "w")
            f.write(data)
            f.close()
            return True
        except:
            return False

    def flush(self):
        pass # not used

    def close(self):
        try:
            if os.access(self.name, os.W_OK):
                os.remove(self.name)
        except:
            pass


### restore from a backup
def kah_restore(data):
    try:
        tf = TmpWorkFile()
        tf.write(data)
        tf.flush()
        kah_proc(["kpsapihelper", "restore", tf.name])
        tf.close()
        return True
    except Exception, e:
        err(str(e))
        return False


### run program, log data if it fails
def kah_proc(cmd):
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        strout, strerr = proc.communicate("")
        ret = proc.returncode

        if ret != 0:
            err("kpsapihelper command: " + " ".join(cmd))
            for s in strout.split("\n"):
                err("kpsapihelper stdout: " + s)
            for s in strerr.split("\n"):
                err("kpsapihelper stderr: " + s)
            raise Exception("kpsapihelper return code: %d" % ( ret ) )

    except Exception, e:
        err("kah_proc: " + str(e))
        raise Exception("kah_proc: " + str(e))


### BEGIN_TESTS ###

def kah_tests():
    print "BEGIN"

    if 0:
        id = kah_get_new_id_act()
        print "NEW ID: " + id + "\n"
        print "\n\n"

        kar = kah_get_kar_act(id, "admin_name", "admin_email", "country", "state", "location", "org", "org_unit", "domain", "email")
        print "KAR IS:\n"
        print kar
        print "\n\n"

        ### can't be tested easily right now
        #status = kah_set_kap_act("0001", "/tmp/kap.bin")
        #print "KAP installed: " + str(status) + "\n"
        #print "\n\n"

    if 1:
        backup = kah_backup()
        print "BACKUP: LEN=" + str(len(backup)) + "\n"

    print "END"


if __name__ == "__main__":
    kah_tests()

### END_TESTS ###


