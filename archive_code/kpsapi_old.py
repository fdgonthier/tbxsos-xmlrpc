### NOT USED / ARCHIVE CODE FOR REFACTORING ONLY ###

# needed only for tests...
# is done with activations kaps
#def addorg(self, sid, name):
#    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
#    db_init()
#    res = sdb_addorg(name)
#    db_commit()
#    return res

def lsorg(self, sid):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    res = sdb_lsorg()
    db_commit()
    return res

#def rmorg(self, sid, orgid):
#    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
#    db_init()
#    res = sdb_rmorg(orgid)
#    db_commit()
#    return res

def setorgforwardto(self, sid, orgid, email):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    try:
        db_init()
        sdb_setorgforwardto(orgid, email)
        db_commit()
    except:
        raise Exception("could not set organization forward_to")
    return True

def addgroup(self, sid, org_id, group_name):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    prof_id = sdb_addgroup(org_id, group_name)
    group_id = sdb_getprofilegroupid(prof_id)
    db_commit()
    return group_id

def lsgroups(self, sid):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    res = sdb_lsprofiles()
    db_commit()
    return res

def rmgroup(self, sid, group_id):
    # no check for profile being a group - just hide the "profiles" notion for this api
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    prof_id = sdb_getgroupprofileid(group_id)
    res = sdb_rmprofile(prof_id)
    db_commit()
    return res

def addldapgroup(self, sid, group_id, group_dn):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    res = sdb_addldapgroup(group_id, group_dn)
    db_commit()
    return res

def getprofilegroupid(self, sid, prof_id):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    res = sdb_getprofilegroupid(prof_id)
    db_commit()
    return res

def lsldapgroups(self, sid, group_id):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    res = sdb_lsldapgroups(group_id)
    db_commit()
    return res

def rmldapgroup(self, sid, ldap_group_id):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    res = sdb_rmldapgroup(ldap_group_id)
    db_commit()
    return res


def get_new_id_act(self, sid):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    res = kah_get_new_id_act()
    return res

def get_kar_act(self, sid, id, admin_name, admin_email, country, state, location, org, org_unit, domain, email):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    res = kah_get_kar_act(id, admin_name, admin_email, country, state, location, org, org_unit, domain, email)
    return res

def set_kap_act(self, sid, id, base64_kap):
    kap = base64.standard_b64decode(base64_kap)
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    res = kah_set_kap_act(id, kap)
    return res

def list_logs(self, sid):
    return os.listdir("/var/log/teambox")

def get_log(self, sid, log_file_name):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    try:
        log_file_path = "/var/log/teambox/%s" % log_file_name
        log_file_stat = os.stat(log_file_path)
        if stat.S_ISREG(log_file_stat[stat.ST_MODE]):
            f = open(log_file_path)
            res = f.read()
            f.close()
            return res
    except Exception, e:
        err(str(e))
        return None

def reboot(self, sid):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
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
            return True
    except Exception, e:
        err(str(e))
        raise

    return False

def backup(self, sid):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    try:
        data = kah_backup()
        b64data = base64.standard_b64encode(data)
        return b64data
    except:
        return None

def restore(self, sid, b64data):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    data = base64.standard_b64decode(b64data)
    try:
        res = kah_restore(data)
        return True
    except:
        return False

def free_login_seat(self, sid, org_id, username):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    res = sdb_freeloginseat(org_id, username)
    db_commit()
    return res

def set_seats_allocation(self, sid, parent_org_id, org_id, number):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    #db_init()
    #res = sdb_setseatsallocation(parent_org_id, org_id, number)
    #db_commit()
    cmd = ["kctl", "setseatsallocation", str(parent_org_id), str(org_id), str(number) ]
    proc = KPopen("", cmd) # "" is data sent to stdin
    if proc.return_code == 0:
        return True
    raise Exception(proc.stderr)

def ls_seats_org(self, sid, org_id):
    session = session_check_load(sid, KAPI_SECURITY_CTX_ADMIN)
    db_init()
    res = sdb_lsseatsorg(org_id)
    db_commit()
    return res

