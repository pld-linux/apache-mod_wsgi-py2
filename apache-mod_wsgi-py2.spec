# TODO:
# - add -n mod_wsgi-express package
#   https://github.com/GrahamDumpleton/mod_wsgi#installation-into-python

%define		mod_name	wsgi
%define		apxs		/usr/sbin/apxs
Summary:	Python 2.x WSGI interface for the Apache Web server
Summary(pl.UTF-8):	Interfejs WSGI Pythona 2.x dla serwera WWW Apache
Name:		apache-mod_%{mod_name}-py2
Version:	4.9.4
Release:	1
License:	Apache
Group:		Networking/Daemons
Source0:	https://github.com/GrahamDumpleton/mod_wsgi/archive/%{version}/mod_%{mod_name}-%{version}.tar.gz
# Source0-md5:	96898152c826fee3b0f36836708383d2
Source1:	%{name}.conf
URL:		http://www.modwsgi.org/
BuildRequires:	%{apxs}
BuildRequires:	apache-devel >= 2.2
BuildRequires:	apr-devel >= 1:1.0.0
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	python-devel >= 1:2.6
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	apache(modules-api) = %{apache_modules_api}
Requires:	apr >= 1:1.0.0
Requires:	python-modules >= 1:2.6
Provides:	apache(mod_wsgi) = %{version}-%{release}
Obsoletes:	apache-mod_wsgi < 4.5.7-0.2
Conflicts:	%{name}-py3
# http://helpful.knobs-dials.com/index.php/Mod_wsgi_notes#PyEval_AcquireThread:_non-NULL_old_thread_state
Conflicts:	apache-mod_python
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)/conf.d

%description
The mod_wsgi adapter is an Apache module that provides a WSGI
compliant interface for hosting Python based web applications within
Apache. The adapter is written completely in C code against the Apache
C runtime and for hosting WSGI applications within Apache has a lower
overhead than using existing WSGI adapters for mod_python or CGI.

%description -l pl.UTF-8
Adapter mod_wsgi jest modułem udostępniającym interfejs WSGI dla
aplikacji WWW napisanych w języku Python i osadzonych w serwerze
Apache. Adapter jest w całości napisany w języku C w oparciu o
bibliotekę uruchomieniową Apache i ma mniejsze wymagania niż w
przypadku używania istniejących adapterów WSGI dla modułu mod_python
lub CGI.

%prep
%setup -q -n mod_%{mod_name}-%{version}

%build
%{__aclocal}
%{__autoconf}
%configure \
	--with-python=%{__python} \
	--with-apxs=%{apxs}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__mv} $RPM_BUILD_ROOT%{_pkglibdir}/mod_%{mod_name}{,-py2}.so
sed -e 's/mod_wsgi.so/mod_wsgi-py2.so/' %{SOURCE1} > $RPM_BUILD_ROOT%{_sysconfdir}/61_mod_wsgi-py2.conf

%clean
rm -rf $RPM_BUILD_ROOT

%triggerpostun -- apache-mod_wsgi < 4.5.7-0.2
if [ -f %{_sysconfdir}/61_mod_wsgi.conf.rpmsave ]; then
	mv -f %{_sysconfdir}/61_mod_wsgi-py2.conf{,.rpmnew}
	mv -f %{_sysconfdir}/61_mod_wsgi{.conf.rpmsave,-py2.conf}
	%{__sed} -i -e 's/mod_wsgi.so/mod_wsgi-py2.so/' $RPM_BUILD_ROOT%{_sysconfdir}/61_mod_wsgi-py2.conf
	%service -q httpd restart
fi

%post
%service -q httpd restart

%postun
if [ "$1" = "0" ]; then
	%service -q httpd restart
fi

%files
%defattr(644,root,root,755)
%doc README.rst CREDITS.rst
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*_mod_%{mod_name}-py2.conf
%attr(755,root,root) %{_pkglibdir}/mod_%{mod_name}-py2.so
