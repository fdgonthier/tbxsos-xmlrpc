#!/usr/bin/python

import sys, os, ConfigParser, time, shutil

stock_config_file_path = "/etc/teambox/kpsapi/kpsapi.ini.stock"
config_file_path = "/etc/teambox/kpsapi/kpsapi.ini"

if os.path.exists(config_file_path):
    # File exists.

    # Instantiate a parser.
    parser = ConfigParser.ConfigParser()

    # Try to parse config.
    try:
        parser.read(config_file_path)
    except:
        print "ERROR: config file '%s' is not parsable... '%s' script cancelled." % ( config_file_path, sys.argv[0] )
        sys.exit(1)

    # Check if config file is ok for that version.
    ok = True
    if parser.has_section("main"):
        try:
            config_version = parser.get("main", "config_version").strip(" ")
            if config_version == "" or float(config_version) < 1:
                ok = False
        except ConfigParser.NoOptionError:
            ok = False
    else:
        ok = False

    if not ok:
        # Overwrite config with stock config.
        backup_file_path = config_file_path + "." + str(int(time.time()))
        shutil.copy(config_file_path, backup_file_path)
        shutil.copy(stock_config_file_path, config_file_path)
        print "KPSAPI config file was not compatible... it has been backed up to '%s' and has been replaced." % \
            ( backup_file_path )

