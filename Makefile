# Works for installing locally or creating a Debian package.
# make install		                # Locally.
# make install DEBIANDIR=$(CURDIR)      # From debian rules.

# For Debian packages.
ifdef DEBIANDIR
	VIRTUALDIR=$(DEBIANDIR)/debian/$(DEBIANPACKAGE)
else
	DEBIANDIR=
	VIRTUALDIR=
endif



install-kpsapi:

# Install misc package stuff in /usr/share/kpsapi/
	mkdir -p $(VIRTUALDIR)/usr/share/kpsapi/
	cp -rf config-stock $(VIRTUALDIR)/usr/share/kpsapi/
	cp -rf www $(VIRTUALDIR)/usr/share/kpsapi/
	cp -rf update_scripts $(VIRTUALDIR)/usr/share/kpsapi/

# Install the lighttpd configuration.
	# Copy to /usr/share/kpsapi/config-stock/ instead and force install in the postinst script.
	#mkdir -p $(VIRTUALDIR)/etc/lighttpd/conf-available
	#cp -f debian/kpsapi.lighttpd.conf \
	#    $(VIRTUALDIR)/etc/lighttpd/conf-available/06-kpsapi.conf
	cp -a debian/kpsapi.lighttpd.conf $(VIRTUALDIR)/usr/share/kpsapi/config-stock/

# Install the CGI stuff.
	mkdir -p $(VIRTUALDIR)/var/www/kpsapi/public/
	install -m755 www/kpsapi.py $(VIRTUALDIR)/var/www/kpsapi/public/kpsapi.py



install:

# Recall this makefile for all packages to install.
	make install-kpsapi DEBIANDIR=$(DEBIANDIR) DEBIANPACKAGE=teambox-kps-xmlrpc

