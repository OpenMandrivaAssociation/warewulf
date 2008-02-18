%define name	warewulf
%define version	2.6.3
%define release	2

Name:		%{name}
Summary:	A cluster implementation and management tool
Version:	%{version}
Release:	%mkrel %{release}
License:	GPLv2+
Group:		System/Servers
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Source0:	http://warewulf.lbl.gov/downloads/releases/%{version}/%{name}-%{version}.tar.gz
Source1:	gzip.c.patch
Patch0:		Makefile.patch
Requires:	dhcp tftp-server nfs-utils perl rsh
Requires:  	%{name}-tools = %{version}-%{release}
Requires:  	perl-Unix-Syslog
Requires:	rpm-helper
ExclusiveOS: 	linux
BuildRequires:	glibc-static-devel
URL:		http://www.perceus.org
Provides: 	perl(Warewulf::Config) 
Provides: 	perl(Warewulf::PXE) 
Provides: 	perl(Warewulf::Util) 

%description
Warewulf is a customizable cluster construction tool that facilitates the
building and administration of clusters. Node updates are fast and
easy to perform because Warewulf distributes an OS image to each node
to boot as a RAM disk when the node is powered on.

This package contains the main component of the Warewulf system; it
contains the monitoring, configuration and node build tools. It should
be installed on the cluster boot server (master).

%package  tools
Summary:  The Warewulf user tools
Group:    System/Configuration/Other
Requires: perl-Term-Screen >= 1.02

%description tools
Warewulf is a customizable cluster construction tool that facilitates the
building and administration of clusters. Node updates are fast and
easy to perform because Warewulf distributes an OS image to each node
to boot as a RAM disk when the node is powered on.

This package provides the Warewulf user tools. It has been separated
from the main package to faciliate the installation of multiple
interactive login nodes and remote monitoring nodes.

%package wulfd
Summary: The Warewulf node daemon
Group:   System/Servers
Requires:  chkconfig

%description wulfd
Warewulf is a customizable cluster construction tool that facilitates the
building and administration of clusters. Node updates are fast and
easy to perform because Warewulf distributes an OS image to each node
to boot as a RAM disk when the node is powered on.

This is the node daemon component of the Warewulf system. 

%package proxy
Summary: The Warewulf node daemon proxy service
Group:   System/Servers
Requires:  chkconfig

%description proxy
Warewulf is a customizable cluster construction tool that facilitates the
building and administration of clusters. Node updates are fast and
easy to perform because Warewulf distributes an OS image to each node
to boot as a RAM disk when the node is powered on.

The wwproxy component aggregates multiple warewulfd daemons together.
It reduces the load on the daemons by only polling each warewulfd at
fixed intervals regardless of how many users are hitting it. It can
also distribute Warewulf node stats in a Ganglia-compatible XML format
suitable for being slurped by gmetad.

%package  web
Summary:  The Warewulf web frontend
Group:    Monitoring
Requires: webserver

%description web
Warewulf is a customizable cluster build tool that facilitates the building
and administration of clusters. It uses RAM disks as the primary media for
storing the nodes distribution so it is fast, volatile, and easily updated.

The web frontend provides an interface to one or more Warewulf clusters.

%prep
%setup -q -n %{name}-%{version} 
%{__cp} -p %{SOURCE1} .
%patch0 -p0

%build
%{__make} %{?mflags}

%install
%{__rm} -Rf %{buildroot}
%{__make} install DESTDIR=$RPM_BUILD_ROOT %{?mflags_install}

%{__mkdir_p} $RPM_BUILD_ROOT/var/warewulf/vnfs
%{__mkdir_p} $RPM_BUILD_ROOT/srv/vnfs

echo "Warewulf release %{version}-%{release}" > \
   $RPM_BUILD_ROOT/etc/warewulf-release

%pre
if rpm -q warewulf | grep 2.4 >/dev/null 2>&1 ; then
   echo "Warewulf %{version} is not intended to update previous versions."
   echo "Backup /etc/warewulf and remove the previous version before"
   echo "installing this version. Reconfigure Warewulf manually by consulting"
   echo "the old configuration saved earlier."
   exit 1
fi

%pre tools
if rpm -q warewulf-tools | grep 2.4 >/dev/null 2>&1 ; then
   echo "Warewulf %{version} is not intended to update previous versions."
   echo "Backup /etc/warewulf and remove the previous version before"
   echo "installing this version. Reconfigure Warewulf manually by consulting"
   echo "the old configuration saved earlier."
   exit 1
fi

%pre wulfd
if rpm -q warewulf-wulfd | grep 2.4 >/dev/null 2>&1 ; then
   echo "Warewulf %{version} is not intended to update previous versions."
   echo "Backup /etc/warewulf and remove the previous version before"
   echo "installing this version. Reconfigure Warewulf manually by consulting"
   echo "the old configuration saved earlier."
   exit 1
fi

%post
%_post_service warewulf
%_post_service vnfsd
%_post_service wwnewd

%post wulfd
%_post_service wulfd

%post web
%__service httpd condrestart >/dev/null 2>&1 ||:
%__service apache2 condrestart >/dev/null 2>&1 ||:

%post proxy
%_post_service wwproxy

%preun
%_preun_service warewulf
%_preun_service vnfsd
%_preun_service wwnewd

%preun wulfd
%_preun_service wulfd

%preun proxy
%_preun_service wwproxy

%postun web
%__service httpd condrestart >/dev/null 2>&1 ||:
%__service apache2 condrestart >/dev/null 2>&1 ||:

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc Readme Copyright Credits Install License Todo
%config() %{_sysconfdir}/warewulf-release
%config(noreplace) %{_sysconfdir}/warewulf/wwinitrd.config
%config(noreplace) %{_sysconfdir}/warewulf/master.conf
%config(noreplace) %{_sysconfdir}/warewulf/vnfs/*
%config(noreplace) %{_sysconfdir}/warewulf/nodes/*
%config(noreplace) %{_sysconfdir}/sysconfig/vnfsd
%config /usr/lib/warewulf/wwinitrc
%config /usr/lib/warewulf/wwpostrc
%dir /srv/vnfs
%dir /var/warewulf
%dir /var/warewulf/vnfs
%dir /var/warewulf/syncs
%dir /usr/lib/warewulf
%dir /usr/lib/warewulf/Warewulf
%dir /usr/lib/warewulf/modules
%dir /usr/share/warewulf
%{_sysconfdir}/rc.d/init.d/warewulf
%{_sysconfdir}/rc.d/init.d/vnfsd
%{_sysconfdir}/rc.d/init.d/wwnewd
/usr/lib/warewulf/Warewulf/*
/usr/lib/warewulf/modules/*
/usr/share/warewulf/*
%{_sbindir}/warewulfd
%{_sbindir}/vnfsd
%{_sbindir}/wwmkinitrd
%{_sbindir}/wwnodes
%{_sbindir}/wwnewd
%{_sbindir}/wwvnfs
%{_sbindir}/wwinit
%{_sbindir}/wwdebug
%{_bindir}/wwps
/var/warewulf/wwinitrd
%{_mandir}/man8/wwinit.8.*
%{_mandir}/man8/wwnodes.8.*
%{_mandir}/man8/wwvnfs.8.*
%{_mandir}/man8/wwmkinitrd.8.*
%{_mandir}/man5/master.conf.5.*

%files tools
%defattr(-,root,root)
%doc Readme Copyright Credits Install License Todo
%config(noreplace) %{_sysconfdir}/warewulf/client.conf
/usr/lib/warewulf/Warewulf/*
%{_bindir}/wwlist
%{_bindir}/wwstats
%{_bindir}/wwsummary
%{_bindir}/wwmpirun
%{_bindir}/wwtop
%{_mandir}/man8/wwlist.8.*
%{_mandir}/man8/wwstats.8.*
%{_mandir}/man8/wwmpirun.8.*
%{_mandir}/man8/wwtop.8.*

%files wulfd
%defattr(-,root,root)
%doc Readme Copyright Credits Install License Todo
%config(noreplace) %{_sysconfdir}/warewulf/node-partitions
%config(noreplace) %{_sysconfdir}/sysconfig/wulfd
%{_sysconfdir}/rc.d/init.d/wulfd
%{_sbindir}/wulfd

%files proxy
%defattr(-,root,root)
%doc Readme Copyright Credits Install License Todo
%config(noreplace) %{_sysconfdir}/sysconfig/wwproxy
%{_sysconfdir}/warewulf/wwproxy.config
%{_sysconfdir}/rc.d/init.d/wwproxy
%{_sbindir}/wwproxy

%files web
%defattr(-,root,root)
%doc Readme Copyright Credits Install License Todo
%config(noreplace) %{_sysconfdir}/httpd/conf.d/warewulf.conf
%{_datadir}/warewulf/cgi
%{_datadir}/warewulf/images
/usr/lib/warewulf/Warewulf/Status.pm

