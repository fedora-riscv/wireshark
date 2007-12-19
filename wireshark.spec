%define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")
#define to 0 for final version
%define svn_version 0
%define with_adns 0

Summary: 	Network traffic analyzer
Name: 		wireshark
Version:	0.99.7
Release: 	1%{?dist}
License: 	GPL+
Group: 		Applications/Internet
%if %{svn_version}
Source0:	http://wireshark.org/download/prerelease/%{name}-%{version}-SVN-%{svn_version}.tar.gz
%else
Source0:	http://wireshark.org/download/src/%{name}-%{version}.tar.gz
%endif
Source1:	wireshark.pam
Source2:	wireshark.console
Source3:	wireshark.desktop
Patch1:		wireshark-0.99.7-pie.patch
Patch3:		wireshark-nfsv4-opts.patch
Url: 		http://www.wireshark.org/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	libpcap-devel >= 0.9
BuildRequires: 	libsmi
BuildRequires: 	zlib-devel, bzip2-devel
BuildRequires:  openssl-devel
BuildRequires:	glib2-devel, gtk2-devel
BuildRequires:  elfutils-devel, krb5-devel
BuildRequires:  python, pcre-devel, libselinux
BuildRequires:  gnutls-devel
BuildRequires:  desktop-file-utils, automake, libtool
BuildRequires:	xdg-utils
%if %{with_adns}
BuildRequires:	adns-devel
%endif
Obsoletes:	ethereal
Provides:	ethereal


%package	gnome
Summary:	Gnome desktop integration for wireshark and wireshark-usermode
Group:		Applications/Internet
Requires: 	gtk2
Requires:	usermode >= 1.37
Requires:	wireshark = %{version}-%{release}
Requires:	libsmi
Requires:	xdg-utils
%if %{with_adns}
Requires:	adns
%endif
Obsoletes:	ethereal-gnome
Provides:	ethereal-gnome


%description
Wireshark is a network traffic analyzer for Unix-ish operating systems.

This package lays base for libpcap, a packet capture and filtering 
library, contains command-line utilities, contains plugins and 
documentation for wireshark. A graphical user interface is packaged 
separately to GTK+ package.

%description gnome
Contains wireshark for Gnome 2 and desktop integration file


%prep
%if %{svn_version}
%setup -q -n %{name}-%{version}-SVN-%{svn_version}
%else
%setup -q -n %{name}-%{version}
%endif
%patch1 -p1 -b .pie
%patch3 -p1 

%build
%ifarch s390 s390x
export PIECFLAGS="-fPIE"
%else
export PIECFLAGS="-fpie"
%endif
# FC5+ automatic -fstack-protector-all switch
export RPM_OPT_FLAGS=${RPM_OPT_FLAGS//-fstack-protector/-fstack-protector-all}
export CFLAGS="$RPM_OPT_FLAGS $CPPFLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS $CPPFLAGS"
export LDFLAGS="$LDFLAGS -lm -lcrypto"
./autogen.sh
%configure \
   --bindir=%{_sbindir} \
   --enable-zlib \
   --enable-ipv6 \
   --with-libsmi \
   --with-gnu-ld \
   --disable-static \
   --disable-usr-local \
   --enable-gtk2 \
   --with-pic \
%if %{with_adns}
   --with-adns \
%else
   --with-adns=no \
%endif
   --with-ssl \
   --disable-warnings-as-errors \
   --with-plugindir=%{_libdir}/%{name}/plugins/%{version}
time make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

# The evil plugins hack
perl -pi -e 's|-L../../epan|-L../../epan/.libs|' plugins/*/*.la

make DESTDIR=$RPM_BUILD_ROOT install

#symlink tshark to tethereal
ln -s tshark $RPM_BUILD_ROOT%{_sbindir}/tethereal

#empty?!
rm -f $RPM_BUILD_ROOT%{_sbindir}/idl2wrs

# install support files for usermode, gnome and kde
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/pam.d
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT/%{_sysconfdir}/pam.d/wireshark
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/security/console.apps
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT/%{_sysconfdir}/security/console.apps/wireshark
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
ln -s consolehelper $RPM_BUILD_ROOT/%{_bindir}/wireshark

# install man
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man1
install -m 644 *.1 $RPM_BUILD_ROOT/%{_mandir}/man1

# Install python stuff.
mkdir -p $RPM_BUILD_ROOT%{python_sitelib}
install -m 644 tools/wireshark_be.py tools/wireshark_gen.py  $RPM_BUILD_ROOT%{python_sitelib}

desktop-file-install --vendor fedora                            \
        --dir ${RPM_BUILD_ROOT}%{_datadir}/applications         \
        --add-category X-Fedora                                 \
        %{SOURCE3}

mkdir -p $RPM_BUILD_ROOT/%{_datadir}/pixmaps
install -m 644 image/wsicon48.png $RPM_BUILD_ROOT/%{_datadir}/pixmaps/wireshark.png


# Remove .la files
rm -f $RPM_BUILD_ROOT/%{_libdir}/%{name}/plugins/%{version}/*.la

# Remove .la files in libdir
rm -f $RPM_BUILD_ROOT/%{_libdir}/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog INSTALL NEWS README* 
%{_sbindir}/editcap
#%{_sbindir}/idl2wrs
%{_sbindir}/tshark
%{_sbindir}/mergecap
%{_sbindir}/text2pcap
%{_sbindir}/dftest
%{_sbindir}/capinfos
%{_sbindir}/randpkt
%{_sbindir}/dumpcap
%{_sbindir}/tethereal
%{python_sitelib}/*
%{_libdir}/lib*
%{_mandir}/man1/editcap.*
%{_mandir}/man1/tshark.*
%{_mandir}/man1/idl2wrs.*
%{_mandir}/man1/mergecap.*
%{_mandir}/man1/text2pcap.*
%{_mandir}/man1/capinfos.*
%{_mandir}/man1/dumpcap.*
%{_mandir}/man4/wireshark-filter.*
%{_libdir}/wireshark
%config(noreplace) %{_sysconfdir}/pam.d/wireshark
%config(noreplace) %{_sysconfdir}/security/console.apps/wireshark
%{_datadir}/wireshark

%files gnome
%defattr(-,root,root)
%{_datadir}/applications/fedora-wireshark.desktop
%{_datadir}/pixmaps/wireshark.png
%{_bindir}/wireshark
%{_sbindir}/wireshark
%{_mandir}/man1/wireshark.*


%changelog
* Tue Dec 18 2007 Radek Vokál <rvokal@redhat.com> 0.99.7-1
- upgrade to 0.99.7
- switch to libsmi from net-snmp
- disable ADNS due to its lack of Ipv6 support

* Wed Sep 19 2007 Radek Vokál <rvokal@redhat.com> 0.99.6-3
- fixed URL

* Thu Aug 23 2007 Radek Vokál <rvokal@redhat.com> 0.99.6-2
- rebuilt

* Mon Jul  9 2007 Radek Vokal <rvokal@redhat.com> 0.99.6-1
- upgrade to 0.99.6 final

* Fri Jun 15 2007 Radek Vokál <rvokal@redhat.com> 0.99.6-0.pre2
- another pre-release
- turn on ADNS support

* Wed May 23 2007 Radek Vokál <rvokal@redhat.com> 0.99.6-0.pre1
- update to pre1 of 0.99.6 release

* Mon Feb  5 2007 Radek Vokál <rvokal@redhat.com> 0.99.5-1
- multiple security issues fixed (#227140)
- CVE-2007-0459 - The TCP dissector could hang or crash while reassembling HTTP packets
- CVE-2007-0459 - The HTTP dissector could crash.
- CVE-2007-0457 - On some systems, the IEEE 802.11 dissector could crash.
- CVE-2007-0456 - On some systems, the LLT dissector could crash.

* Mon Jan 15 2007 Radek Vokal <rvokal@redhat.com> 0.99.5-0.pre2
- another 0.99.5 prerelease, fix build bug and pie flags

* Tue Dec 12 2006 Radek Vokal <rvokal@redhat.com> 0.99.5-0.pre1
- update to 0.99.5 prerelease

* Thu Dec  7 2006 Jeremy Katz <katzj@redhat.com> - 0.99.4-5
- rebuild for python 2.5 

* Tue Nov 28 2006 Radek Vokal <rvokal@redhat.com> 0.99.4-4
- rebuilt for new libpcap and net-snmp

* Thu Nov 23 2006 Radek Vokal <rvokal@redhat.com> 0.99.4-3
- add htmlview to Buildrequires to be picked up by configure scripts (#216918)

* Tue Nov  7 2006 Radek Vokal <rvokal@redhat.com> 0.99.4-2.fc7
- Requires: net-snmp for the list of MIB modules 

* Wed Nov  1 2006 Radek Vokál <rvokal@redhat.com> 0.99.4-1
- upgrade to 0.99.4 final

* Tue Oct 31 2006 Radek Vokál <rvokal@redhat.com> 0.99.4-0.pre2
- upgrade to 0.99.4pre2

* Tue Oct 10 2006 Radek Vokal <rvokal@redhat.com> 0.99.4-0.pre1
- upgrade to 0.99.4-0.pre1

* Fri Aug 25 2006 Radek Vokál <rvokal@redhat.com> 0.99.3-1
- upgrade to 0.99.3
- Wireshark 0.99.3 fixes the following vulnerabilities:
- the SCSI dissector could crash. Versions affected: CVE-2006-4330
- the IPsec ESP preference parser was susceptible to off-by-one errors. CVE-2006-4331
- a malformed packet could make the Q.2931 dissector use up available memory. CVE-2006-4333 

* Tue Jul 18 2006 Radek Vokál <rvokal@redhat.com> 0.99.2-1
- upgrade to 0.99.2

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.99.2-0.pre1.1
- rebuild

* Tue Jul 11 2006 Radek Vokál <rvokal@redhat.com> 0.99.2-0.pre1
- upgrade to 0.99.2pre1, fixes (#198242)

* Tue Jun 13 2006 Radek Vokal <rvokal@redhat.com> 0.99.1-0.pre1
- spec file changes

* Fri Jun  9 2006 Radek Vokal <rvokal@redhat.com> 0.99.1pre1-1
- initial build for Fedora Core
