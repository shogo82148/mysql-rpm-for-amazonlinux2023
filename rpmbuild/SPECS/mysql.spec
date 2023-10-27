# Copyright (c) 2000, 2023, Oracle and/or its affiliates.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2.0,
# as published by the Free Software Foundation.
#
# This program is also distributed with certain software (including
# but not limited to OpenSSL) that is licensed under separate terms,
# as designated in a particular file or component or in included license
# documentation.  The authors of MySQL hereby grant you an additional
# permission to link the program and your derivative works with the
# separately licensed software that they have included with MySQL.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License, version 2.0, for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA

# NOTE: "vendor" is used in upgrade/downgrade check, so you can't
# change these, has to be exactly as is.

%global mysql_vendor Oracle and/or its affiliates
%global mysqldatadir /var/lib/mysql

# Pass --define 'with_cluster 1' to build with cluster support
%{?with_cluster: %global cluster 1}

%if 0%{?cluster}
%global with_meb    0
%global with_router 0
%else
%if 0%{?commercial}
%global with_meb    1
%else
%global with_meb    0
%endif
%global with_router 1
%endif

# Pass path to mecab lib
%{?with_mecab: %global mecab_option -DWITH_MECAB=%{with_mecab}}
%{?with_mecab: %global mecab 1}

# Pass path to the AWS SDK install
%{?with_aws_sdk: %global aws_sdk_option -DWITH_KEYRING_AWS=1 -DWITH_AWS_SDK=%{with_aws_sdk}}
%{?with_aws_sdk: %global aws_sdk 1}

%global ssl_default 1

# Pass alternative ssl setting if provided. Can be used for newer OpenSSL.
%{?with_ssl: %global ssl_option -DWITH_SSL=%{with_ssl}}
%{?with_ssl: %global ssl_bundled 1}

# Use OpenSSL 1.1
%{?with_openssl11: %global ssl_option -DWITH_SSL=openssl11}
%{?with_openssl11: %global ssl_default 0}

# Tell build not to use minimal debug
%{?full_debug: %global no_mini_debug 1}

# Regression tests may take a long time, override the default to skip them
%{!?runselftest:%global runselftest 0}

%{!?with_systemd:                %global systemd 0}
%{?el7:                          %global systemd 1}
%{?el8:                          %global systemd 1}
%{?el9:                          %global systemd 1}
%{?amzn2023:                     %global systemd 1}

%if 0%{?rhel} >= 8
%global add_fido_plugins 1
%else
%global add_fido_plugins 0
%endif # rhel8 or above

# Two workarounds on el6 and el7
%if 0%{?rhel} == 6 || 0%{?rhel} == 7
# - Avoid compiling Python 3 code with Python 2
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
# - Ship debuginfo for community
%if 0%{?commercial}
%if 0%{?no_mini_debug}
%else
%global mini_debug_option -DMINIMAL_RELWITHDEBINFO=1
%endif # no_mini_debug
%else
%global with_debuginfo 1
%endif # commercial
%endif # rhel6|7

%{?el8:                          %global with_debuginfo 1}
%{?el9:                          %global with_debuginfo 1}
%{!?with_debuginfo:              %global without_debuginfo 1}

%{!?product_suffix:              %global product_suffix community}
%{!?feature_set:                 %global feature_set community}
%{!?compilation_comment_release: %global compilation_comment_release MySQL Community - GPL}
%{!?compilation_comment_debug:   %global compilation_comment_debug MySQL Community - GPL - Debug}
%{!?compilation_comment_server_release: %global compilation_comment_server_release MySQL Community Server - GPL}
%{!?compilation_comment_server_debug:   %global compilation_comment_server_debug MySQL Community Server - GPL - Debug}
%{!?src_base:                    %global src_base mysql%{?cluster:-cluster-gpl}}

%if 0%{?rhel} == 6
%global compatver             5.1.73
%global compatlib             16
%global compatsrc             https://cdn.mysql.com/Downloads/MySQL-5.1/mysql-%{compatver}.tar.gz
%endif

%if 0%{?rhel} == 7
%global compatver             5.6.51
%global compatlib             18
%global compatsrc             https://cdn.mysql.com/Downloads/MySQL-5.6/mysql-%{compatver}.tar.gz
%endif

%global cmake3                cmake%{?el6:3}%{?el7:3}

# multiarch
%global multiarchs            ppc %{power64} %{ix86} x86_64 %{sparc}

%global src_dir               %{src_base}-8.0.35

%if 0%{?without_debuginfo}
%global _enable_debug_package 0
%global debug_package         %{nil}
%global __os_install_post     /usr/lib/rpm/brp-compress %{nil}
%endif

%global license_files_server  %{src_dir}/LICENSE %{src_dir}/README

%if 0%{?commercial}
%global license_type          Commercial
%else
%global license_type          GPLv2
%endif

%global min                   8.0.11

Name:           mysql%{?cluster:-cluster}-%{product_suffix}
Summary:        A very fast and reliable SQL database server
Group:          Applications/Databases
Version:        8.0.35
Release:        1%{?commercial:.1}%{?dist}
License:        Copyright (c) 2000, 2023, %{mysql_vendor}. Under %{?license_type} license as shown in the Description field.
Source0:        https://cdn.mysql.com/Downloads/MySQL-8.0/%{src_dir}.tar.gz
URL:            http://www.mysql.com/
Packager:       MySQL Release Engineering <mysql-build@oss.oracle.com>
Vendor:         %{mysql_vendor}
%if 0%{?compatlib}
Source7:        %{compatsrc}
%endif
Source10:       https://boostorg.jfrog.io/artifactory/main/release/1.77.0/source/boost_1_77_0.tar.bz2
Source90:       filter-provides.sh
Source91:       filter-requires.sh
%if 0%{?rhel} >= 8
BuildRequires:  cmake >= 3.6.1
BuildRequires:  libtirpc-devel
BuildRequires:  rpcgen
%else
BuildRequires:  cmake3 >= 3.6.1
%endif
%{?el6:BuildRequires:  devtoolset-8-gcc}
%{?el6:BuildRequires:  devtoolset-8-gcc-c++}
%{?el6:BuildRequires:  devtoolset-8-binutils}
%ifarch aarch64
%{?el7:BuildRequires:  devtoolset-10-gcc}
%{?el7:BuildRequires:  devtoolset-10-gcc-c++}
%{?el7:BuildRequires:  devtoolset-10-binutils}
%else
%{?el7:BuildRequires:  devtoolset-11-gcc}
%{?el7:BuildRequires:  devtoolset-11-gcc-c++}
%{?el7:BuildRequires:  devtoolset-11-binutils}
%endif
%{?el8:BuildRequires:  gcc-toolset-12-annobin-annocheck}
%{?el8:BuildRequires:  gcc-toolset-12-annobin-plugin-gcc}
%{?el8:BuildRequires:  gcc-toolset-12-binutils}
%{?el8:BuildRequires:  gcc-toolset-12-gcc-c++}
%{?el8:BuildRequires:  gcc-toolset-12-gcc}
%{?el9:BuildRequires:  gcc-toolset-12-annobin-annocheck}
%{?el9:BuildRequires:  gcc-toolset-12-annobin-plugin-gcc}
%{?el9:BuildRequires:  gcc-toolset-12-binutils}
%{?el9:BuildRequires:  gcc-toolset-12-gcc-c++}
%{?el9:BuildRequires:  gcc-toolset-12-gcc}
BuildRequires:  bison >= 2.1
BuildRequires:  elfutils
BuildRequires:  perl
%{?el7:BuildRequires: perl(Env)}
%{?el8:BuildRequires: perl(Env)}
%{?el9:BuildRequires: perl(Env)}
BuildRequires:  perl(Carp)
BuildRequires:  perl(Config)
BuildRequires:  perl(Cwd)
BuildRequires:  perl(Data::Dumper)
BuildRequires:  perl(English)
BuildRequires:  perl(Errno)
BuildRequires:  perl(Exporter)
BuildRequires:  perl(Fcntl)
BuildRequires:  perl(File::Basename)
BuildRequires:  perl(File::Copy)
BuildRequires:  perl(File::Find)
BuildRequires:  perl(File::Path)
BuildRequires:  perl(File::Spec)
BuildRequires:  perl(File::Spec::Functions)
BuildRequires:  perl(File::Temp)
BuildRequires:  perl(Getopt::Long)
BuildRequires:  perl(IO::File)
BuildRequires:  perl(IO::Handle)
BuildRequires:  perl(IO::Pipe)
BuildRequires:  perl(IO::Select)
BuildRequires:  perl(IO::Socket)
BuildRequires:  perl(IO::Socket::INET)
BuildRequires:  perl(JSON)
BuildRequires:  perl(Memoize)
BuildRequires:  perl(POSIX)
BuildRequires:  perl(Sys::Hostname)
BuildRequires:  perl(Time::HiRes)
BuildRequires:  perl(Time::localtime)
BuildRequires:  time
BuildRequires:  libaio-devel
%if 0%{?commercial}
BuildRequires:  cyrus-sasl-gssapi
%{?el7:BuildRequires: cyrus-sasl-scram}
%{?el8:BuildRequires: cyrus-sasl-scram}
%{?el9:BuildRequires: cyrus-sasl-scram}
BuildRequires:  libcurl-devel
%endif
BuildRequires:  krb5-devel
BuildRequires:  ncurses-devel
BuildRequires:  numactl-devel
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel
%if 0%{?with_openssl11}
BuildRequires:  openssl11-devel
%endif
%if 0%{?systemd}
BuildRequires:  systemd
BuildRequires:  pkgconfig(systemd)
%endif
BuildRequires:  cyrus-sasl-devel
BuildRequires:  openldap-devel
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if 0%{?rhel} > 6
# For rpm => 4.9 only: https://fedoraproject.org/wiki/Packaging:AutoProvidesAndRequiresFiltering
%global _privatelibs libprotobuf.*|libmysqlharness\.so.*|libmysqlharness_stdx\.so.*|libmysqlharness_tls\.so.*|libmysqlrouter\.so\..*|libmysqlrouter_.*\.so\..*%{?ssl_bundled:|libssl\.so\..*|libcrypto\.so\..*}|libfido2.*
%global _privateperl perl\\((GD|hostnames|lib::mtr|lib::v1|mtr_|My::)
%global __requires_exclude ^((%{_privatelibs})|(%{_privateperl}))
%global __provides_exclude_from ^(/usr/share/(mysql|mysql-test)/.*|%{_libdir}/mysql/plugin/.*\\.so|%{_libdir}/mysql/private/.*|%{_libdir}/mysqlrouter/.*|%{_libdir}/mysqlrouter/private/.*)$
%else
# https://fedoraproject.org/wiki/EPEL:Packaging#Generic_Filtering_on_EPEL6
%global __perl_provides %{SOURCE90}
%global __perl_requires %{SOURCE91}
%endif

%description
The MySQL(TM) software delivers a very fast, multi-threaded, multi-user,
and robust SQL (Structured Query Language) database server. MySQL Server
is intended for mission-critical, heavy-load production systems as well
as for embedding into mass-deployed software. MySQL is a trademark of
%{mysql_vendor}

The MySQL software has Dual Licensing, which means you can use the MySQL
software free of charge under the GNU General Public License
(http://www.gnu.org/licenses/). You can also purchase commercial MySQL
licenses from %{mysql_vendor} if you do not wish to be bound by the terms of
the GPL. See the chapter "Licensing and Support" in the manual for
further info.

The MySQL web site (http://www.mysql.com/) provides the latest
news and information about the MySQL software. Also please see the
documentation and the manual for more information.

%package        server
Summary:        A very fast and reliable SQL database server
Group:          Applications/Databases
Requires:       coreutils
Requires:       grep
Requires:       procps
Requires:       shadow-utils
Requires:       net-tools
Requires:       %{name}-client%{?_isa} >= %{min}
Requires:       %{name}-common%{?_isa} = %{version}-%{release}
Requires:       %{name}-icu-data-files = %{version}-%{release}
%if 0%{?commercial}
Obsoletes:      mysql-commercial-bench < 5.7.8
Obsoletes:      mysql-commercial-embedded < 8.0.1
Obsoletes:      mysql-commercial-embedded-devel < 8.0.1
Provides:       MySQL-server-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-server-advanced < %{version}-%{release}
Obsoletes:      MySQL-embedded-advanced < %{version}-%{release}
Obsoletes:      mysql-community-server < %{version}-%{release}
%if 0%{?without_debuginfo}
Obsoletes:      mysql-community-server-debug < %{version}-%{release}
%endif
%if 0%{?cluster}
Provides:       MySQL-Cluster-server-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-server-advanced < %{version}-%{release}
Obsoletes:      MySQL-Cluster-embedded-advanced < %{version}-%{release}
Obsoletes:      mysql-commercial-server < %{version}-%{release}
Obsoletes:      mysql-cluster-community-server < %{version}-%{release}
%if 0%{?without_debuginfo}
Obsoletes:      mysql-cluster-community-server-debug < %{version}-%{release}
%endif
Obsoletes:      mysql-cluster-commercial-embedded < 8.0.1
Obsoletes:      mysql-cluster-commercial-embedded-devel < 8.0.1
%endif
%endif
%if 0%{?cluster}
Provides:       MySQL-Cluster-server-gpl%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-server-gpl < %{version}-%{release}
Obsoletes:      mysql-cluster-community-embedded < 8.0.1
Obsoletes:      mysql-cluster-community-embedded-devel < 8.0.1
Obsoletes:      MySQL-Cluster-embedded-gpl < %{version}-%{release}
%endif
Provides:       MySQL-server%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-server < %{version}-%{release}
Obsoletes:      mysql-community-bench < 5.7.8
Obsoletes:      mysql-community-embedded < 8.0.1
Obsoletes:      mysql-community-embedded-devel < 8.0.1
Obsoletes:      mysql-embedded-devel < 8.0.1
Obsoletes:      community-mysql-bench
Obsoletes:      mysql-bench
Obsoletes:      mysql-server < %{version}-%{release}
Obsoletes:      mariadb-connector-c-config
Obsoletes:      mariadb-backup
Obsoletes:      mariadb-bench
Obsoletes:      mariadb-server
Obsoletes:      mariadb-server-galera
Obsoletes:      mariadb-server-utils
Obsoletes:      mariadb-galera-server
Obsoletes:      mariadb-gssapi-server
Obsoletes:      mariadb-oqgraph-engine
Provides:       mysql-server = %{version}-%{release}
Provides:       mysql-server%{?_isa} = %{version}-%{release}
Provides:       mysql-compat-server = %{version}-%{release}
Provides:       mysql-compat-server%{?_isa} = %{version}-%{release}
%if 0%{?systemd}
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
%else
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/chkconfig
Requires(preun):  /sbin/service
%endif

%description    server
The MySQL(TM) software delivers a very fast, multi-threaded, multi-user,
and robust SQL (Structured Query Language) database server. MySQL Server
is intended for mission-critical, heavy-load production systems as well
as for embedding into mass-deployed software. MySQL is a trademark of
%{mysql_vendor}

The MySQL software has Dual Licensing, which means you can use the MySQL
software free of charge under the GNU General Public License
(http://www.gnu.org/licenses/). You can also purchase commercial MySQL
licenses from %{mysql_vendor} if you do not wish to be bound by the terms of
the GPL. See the chapter "Licensing and Support" in the manual for
further info.

The MySQL web site (http://www.mysql.com/) provides the latest news and
information about the MySQL software.  Also please see the documentation
and the manual for more information.

This package includes the MySQL server binary as well as related utilities
to run and administer a MySQL server.

%if 0%{?with_debuginfo}
%package        server-debug
Summary:        The debug version of MySQL server
Requires:       %{name}-server = %{version}-%{release}
%if 0%{?commercial}
Obsoletes:      mysql-community-server-debug < %{version}-%{release}
%if 0%{?cluster}
Obsoletes:      mysql-commercial-server-debug < %{version}-%{release}
Obsoletes:      mysql-cluster-community-server-debug < %{version}-%{release}
%endif # cluster
%else
%if 0%{?cluster}
Obsoletes:      mysql-community-server-debug < %{version}-%{release}
%endif # cluster
%endif # commercial

%description    server-debug
This packages contains the special debug build of MySQL server.
%endif # with_debuginfo

%package        client
Summary:        MySQL database client applications and tools
Group:          Applications/Databases
Requires:       %{name}-libs%{?_isa} >= %{min}
Requires:       %{name}-client-plugins = %{version}-%{release}
%if 0%{?commercial}
Provides:       MySQL-client-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-client-advanced < %{version}-%{release}
Obsoletes:      mysql-community-client < %{version}-%{release}
%if 0%{?cluster}
Provides:       MySQL-Cluster-client-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-client-advanced < %{version}-%{release}
Obsoletes:      mysql-commercial-client < %{version}-%{release}
Obsoletes:      mysql-cluster-community-client < %{version}-%{release}
%endif
%endif
%if 0%{?cluster}
Provides:       MySQL-Cluster-client-gpl%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-client-gpl < %{version}-%{release}
%endif
Provides:       MySQL-client%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-client < %{version}-%{release}
Obsoletes:      mariadb
Obsoletes:      mysql < %{version}-%{release}
Provides:       mysql = %{version}-%{release}
Provides:       mysql%{?_isa} = %{version}-%{release}

%description    client
This package contains the standard MySQL clients and administration
tools.

%package        icu-data-files
Summary:        MySQL packaging of ICU data files

%description    icu-data-files
This package contains ICU data files needer by MySQL regular expressions.

%package        common
Summary:        MySQL database common files for server and client libs
Group:          Applications/Databases
%if 0%{?commercial}
Obsoletes:      mysql-community-common < %{version}-%{release}
%if 0%{?cluster}
Obsoletes:      mysql-commercial-common < %{version}-%{release}
Obsoletes:      mysql-cluster-community-common < %{version}-%{release}
%endif
%endif
Provides:       mysql-common = %{version}-%{release}
Provides:       mysql-common%{?_isa} = %{version}-%{release}

%description    common
This packages contains common files needed by MySQL client library and
MySQL database server.

%package        test
Summary:        Test suite for the MySQL database server
Group:          Applications/Databases
Requires:       %{name}-server%{?_isa} >= %{min}
Requires:       perl(Carp)
Requires:       perl(Config)
Requires:       perl(Cwd)
Requires:       perl(Data::Dumper)
Requires:       perl(English)
Requires:       perl(Errno)
Requires:       perl(Exporter)
Requires:       perl(Fcntl)
Requires:       perl(File::Basename)
Requires:       perl(File::Copy)
Requires:       perl(File::Find)
Requires:       perl(File::Path)
Requires:       perl(File::Spec)
Requires:       perl(File::Spec::Functions)
Requires:       perl(File::Temp)
Requires:       perl(Getopt::Long)
Requires:       perl(IO::File)
Requires:       perl(IO::Handle)
Requires:       perl(IO::Pipe)
Requires:       perl(IO::Select)
Requires:       perl(IO::Socket)
Requires:       perl(IO::Socket::INET)
Requires:       perl(JSON)
Requires:       perl(Memoize)
Requires:       perl(POSIX)
Requires:       perl(Sys::Hostname)
Requires:       perl(Time::HiRes)
Requires:       perl(Time::localtime)
%if 0%{?cluster}
Requires:       %{name}-data-node%{?_isa} >= %{min}
Requires:       %{name}-management-server%{?_isa} >= %{min}
%endif
%if 0%{?commercial}
Provides:       MySQL-test-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-test-advanced < %{version}-%{release}
Obsoletes:      mysql-community-test < %{version}-%{release}
%if 0%{?cluster}
Provides:       MySQL-Cluster-test-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-test-advanced < %{version}-%{release}
Obsoletes:      mysql-commercial-test < %{version}-%{release}
Obsoletes:      mysql-cluster-community-test < %{version}-%{release}
%endif
%endif
%if 0%{?cluster}
Provides:       MySQL-Cluster-test-gpl%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-test-gpl < %{version}-%{release}
%endif
Provides:       MySQL-test%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-test < %{version}-%{release}
Obsoletes:      mysql-test < %{version}-%{release}
Obsoletes:      mariadb-test
Provides:       mysql-test = %{version}-%{release}
Provides:       mysql-test%{?_isa} = %{version}-%{release}

%description    test
This package contains the MySQL regression test suite for MySQL
database server.

%package        devel
Summary:        Development header files and libraries for MySQL database client applications
Group:          Applications/Databases
Requires:       %{name}-libs%{?_isa} >= %{min}
%if 0%{?commercial}
Provides:       MySQL-devel-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-devel-advanced < %{version}-%{release}
Obsoletes:      mysql-community-devel < %{version}-%{release}
%if 0%{?cluster}
Provides:       MySQL-Cluster-devel-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-devel-advanced < %{version}-%{release}
Obsoletes:      mysql-commercial-devel < %{version}-%{release}
Obsoletes:      mysql-cluster-community-devel < %{version}-%{release}
%endif
%endif
%if 0%{?cluster}
Provides:       MySQL-Cluster-devel-gpl%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-devel-gpl < %{version}-%{release}
%endif
Provides:       MySQL-devel = %{version}-%{release}
Obsoletes:      MySQL-devel < %{version}-%{release}
Obsoletes:      mysql-devel < %{version}-%{release}
%{?el8:Obsoletes:      mariadb-embedded-devel}
%{?el9:Obsoletes:      mariadb-embedded-devel}
Obsoletes:      mariadb-devel
Obsoletes:      mariadb-connector-c-devel
Obsoletes:      mysql-connector-c-devel < 6.2
Provides:       mysql-devel = %{version}-%{release}
Provides:       mysql-devel%{?_isa} = %{version}-%{release}

%description    devel
This package contains the development header files and libraries necessary
to develop MySQL client applications.

%package        libs
Summary:        Shared libraries for MySQL database client applications
Group:          Applications/Databases
Requires:       %{name}-common%{?_isa} >= %{min}
Requires:       %{name}-client-plugins = %{version}-%{release}
%if 0%{?commercial}
Provides:       MySQL-shared-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-shared-advanced < %{version}-%{release}
Obsoletes:      mysql-community-libs < %{version}-%{release}
%if 0%{?cluster}
Provides:       MySQL-Cluster-shared-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-shared-advanced < %{version}-%{release}
Obsoletes:      MySQL-shared-advanced < %{version}-%{release}
Obsoletes:      mysql-cluster-community-libs < %{version}-%{release}
%endif
%endif
%if 0%{?cluster}
Provides:       MySQL-Cluster-shared-gpl%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-shared-gpl < %{version}-%{release}
%endif
Provides:       MySQL-shared%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-shared < %{version}-%{release}
Obsoletes:      mysql-libs < %{version}-%{release}
Obsoletes:      mariadb-libs
Obsoletes:      mysql-connector-c-shared < 6.2
Provides:       mysql-libs = %{version}-%{release}
Provides:       mysql-libs%{?_isa} = %{version}-%{release}

%description    libs
This package contains the shared libraries for MySQL client
applications.

%package        client-plugins
Summary:        Shared plugins for MySQL client applications
Group:          Applications/Databases
Provides:       mysql-client-plugins = %{version}-%{release}
%if 0%{?commercial}
Conflicts:      mysql-commercial-server < 8.0.21
Conflicts:      mysql-commercial-client < 8.0.22
Obsoletes:      mysql-community-client-plugins < %{version}-%{release}
%if 0%{?cluster}
Obsoletes:      mysql-commercial-client-plugins < %{version}-%{release}
Conflicts:      mysql-cluster-commercial-server < 8.0.21
Conflicts:      mysql-cluster-commercial-client < 8.0.22
Obsoletes:      mysql-community-client-plugins < %{version}-%{release}
Obsoletes:      mysql-commercial-client-plugins < %{version}-%{release}
%endif
%else
Conflicts:      mysql-community-server < 8.0.21
Conflicts:      mysql-community-client < 8.0.22
%if 0%{?cluster}
Conflicts:      mysql-cluster-community-server < 8.0.21
Conflicts:      mysql-cluster-community-client < 8.0.22
Obsoletes:      mysql-community-client-plugins < %{version}-%{release}
%endif
%endif

%description    client-plugins
This package contains the client-plugins libraries used by MySQL client applications.


%if 0%{?compatlib}
%package        libs-compat
Summary:        Shared compat libraries for MySQL %{compatver} database client applications
Group:          Applications/Databases
Obsoletes:      mysql-libs-compat < %{version}-%{release}
Provides:       mysql-libs-compat = %{version}-%{release}
Provides:       mysql-libs-compat%{?_isa} = %{version}-%{release}
Requires:       %{name}-libs%{?_isa} >= %{min}
%if 0%{?commercial}
Provides:       MySQL-shared-compat-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-shared-compat-advanced < %{version}-%{release}
Obsoletes:      mysql-community-libs-compat < %{version}-%{release}
%if 0%{?cluster}
Provides:       MySQL-Cluster-shared-compat-advanced%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-shared-compat-advanced < %{version}-%{release}
Obsoletes:      mysql-commercial-libs-compat < %{version}-%{release}
Obsoletes:      mysql-cluster-community-libs-compat < %{version}-%{release}
%endif
%endif
%if 0%{?cluster}
Provides:       MySQL-Cluster-shared-compat-gpl%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-Cluster-shared-compat-gpl < %{version}-%{release}
%endif
Provides:       MySQL-shared-compat%{?_isa} = %{version}-%{release}
Obsoletes:      MySQL-shared-compat < %{version}-%{release}
Obsoletes:      mysql-libs < %{version}-%{release}
Obsoletes:      mariadb-libs

%description    libs-compat
This package contains the shared compat libraries for MySQL %{compatver} client
applications.
%endif

%if 0%{?rhel} == 7
%package        embedded-compat
Summary:        MySQL embedded compat library
Group:          Applications/Databases
Requires:       %{name}-common%{?_isa} >= %{min}
%if 0%{?commercial}
Obsoletes:      mysql-community-embedded-compat < %{version}-%{release}
%if 0%{?cluster}
Obsoletes:      mysql-commercial-embedded-compat < %{version}-%{release}
Obsoletes:      mysql-cluster-community-embedded-compat < %{version}-%{release}
%endif
%endif
Obsoletes:      MySQL-embedded < %{version}-%{release}
Obsoletes:      mysql-embedded < %{version}-%{release}
Obsoletes:      mysql-embedded-devel < %{version}-%{release}
Obsoletes:      mariadb-embedded
Obsoletes:      mariadb-embedded-devel

%description    embedded-compat
This package contains the MySQL server as an embedded library with
compatibility for applications using version %{compatlib} of the library.
%endif

%if 0%{?with_router}
%package  -n   mysql-router-%{product_suffix}
Summary:       MySQL Router
Group:         Applications/Databases
Provides:      mysql-router = %{version}-%{release}
Obsoletes:     mysql-router < %{version}-%{release}
%{?el7:Requires:  openssl-libs >= 1.0.2j}
%if 0%{?commercial}
Obsoletes:     mysql-router-community < %{version}-%{release}
%endif
%description -n mysql-router-%{product_suffix}
The MySQL(TM) Router software delivers a fast, multi-threaded way of
routing connections from MySQL Clients to MySQL Servers. MySQL is a
trademark of Oracle.

The MySQL software has Dual Licensing, which means you can use the
MySQL software free of charge under the GNU General Public License
(http://www.gnu.org/licenses/). You can also purchase commercial MySQL
licenses from Oracle and/or its affiliates if you do not wish to be
bound by the terms of the GPL. See the chapter "Licensing and Support"
in the manual for further info.

The MySQL web site (http://www.mysql.com/) provides the latest news
and information about the MySQL software. Also please see the
documentation and the manual for more information.

%package   -n   mysql-router-%{product_suffix}-devel
Summary:        Development header files and libraries for MySQL Router
Group:          Applications/Databases
Provides:       mysql-router-devel = %{version}-%{release}
Obsoletes:      mysql-router-devel < %{version}-%{release}
%if 0%{?commercial}
Obsoletes:      mysql-router-community-devel < %{version}-%{release}
Requires:       mysql-router-commercial = %{version}-%{release}
%else
Requires:       mysql-router-community = %{version}-%{release}
%endif
%description -n mysql-router-%{product_suffix}-devel
This package contains the development header files and libraries
necessary to develop MySQL Router applications.
%endif # with_router

%if 0%{?cluster}
%package        management-server
Summary:        MySQL Cluster Management Server Daemon
Group:          Applications/Databases
%description    management-server
This package contains the MySQL Cluster Management Server Daemon,
which reads the cluster configuration file and distributes this
information to all nodes in the cluster.

%package        data-node
Summary:        MySQL Cluster Data Node Daemon
Group:          Applications/Databases
%description    data-node
This package contains MySQL Cluster Data Node Daemon, it is the process
that is used to handle all the data in tables using the NDB Cluster
storage engine. It comes in two variants: ndbd and ndbmtd, the former
is single threaded while the latter is multi-threaded.

%package        ndbclient
Summary:        Shared libraries for MySQL NDB storage engine client applications
Group:          Applications/Databases
%description    ndbclient
This package contains the shared libraries for MySQL MySQL NDB storage
engine client applications.

%package        ndbclient-devel
Summary:        Development files for MySQL NDB storage engine client applications
Group:          Applications/Databases
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
Requires:       %{name}-ndbclient%{?_isa} = %{version}-%{release}
%description    ndbclient-devel
This package contains the development header files and libraries
necessary to develop client applications for MySQL NDB storage engine.

%if 0%{?ndb_nodejs_extras_path:1}
%package        nodejs
Summary:        Set of Node.js adapters for MySQL Cluster
Group:          Applications/Databases
%description    nodejs
This package contains MySQL NoSQL Connector for JavaScript, a set of
Node.js adapters for MySQL Cluster and MySQL Server, which make it
possible to write JavaScript applications for Node.js using MySQL
data.
%endif

%package        java
Summary:        MySQL Cluster Connector for Java
Group:          Applications/Databases
%description    java
This package contains MySQL Cluster Connector for Java, which includes
ClusterJ and ClusterJPA, a plugin for use with OpenJPA.

ClusterJ is a high level database API that is similar in style and
concept to object-relational mapping persistence frameworks such as
Hibernate and JPA.

ClusterJPA is an OpenJPA implementation for MySQL Cluster that
attempts to offer the best possible performance by leveraging the
strengths of both ClusterJ and JDBC.

%endif # cluster

%if 0%{?with_meb}
%package        backup
Summary:        MySQL Enterprise Backup
Group:          Applications/Databases
Provides:       meb = %{version}-%{release}
Provides:       meb%{?_isa} = %{version}-%{release}
Obsoletes:      meb < %{version}-%{release}
%description    backup
Implementing proper database backup and disaster recovery plans to
protect against accidental loss of data, database corruption,
hardware/operating system crashes orany natural disasters has become
one of the most important responsibilities of the Database
Administrator (DBAs).

MySQL Enterprise Backup provides DBAs with a high-performance, online
"hot" backup solution with data compression technology to ensure your
data is protected in case of downtime or an outage. MySQL is a
trademark of %{mysql_vendor}
%endif # with_meb

%prep
%if 0%{?compatlib}
%setup -q -T -a 0 -a 7 -a 10 -c -n %{src_dir}
%else
%setup -q -T -a 0 -a 10 -c -n %{src_dir}
%endif # 0%{?compatlib}

%build
# Fail quickly and obviously if user tries to build as root
%if 0%{?runselftest}
if [ "x$(id -u)" = "x0" ] ; then
   echo "The MySQL regression tests may fail if run as root."
   echo "If you really need to build the RPM as root, use"
   echo "--define='runselftest 0' to skip the regression tests."
   exit 1
fi
%endif

# Build compat libs
%if 0%{?compatlib}
%if 0%{?rhel} < 7
(
  export CFLAGS="%{optflags} -D_GNU_SOURCE -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -fno-strict-aliasing -fwrapv"
  export CXXFLAGS="$CFLAGS %{?el6:-felide-constructors} -fno-rtti -fno-exceptions"
  pushd mysql-%{compatver}
  %configure \
    --with-readline \
    --without-debug \
    --enable-shared \
    --localstatedir=/var/lib/mysql \
    --with-unix-socket-path=/var/lib/mysql/mysql.sock \
    --with-mysqld-user="mysql" \
    --with-extra-charsets=all \
    --enable-local-infile \
    --enable-largefile \
    --enable-thread-safe-client \
    --with-ssl=%{_prefix} \
    --with-embedded-server \
    --with-big-tables \
    --with-pic \
    --with-plugin-innobase \
    --with-plugin-innodb_plugin \
    --with-plugin-partition \
    --disable-dependency-tracking
  make %{?_smp_mflags}
  popd
)
%else  # 0%{?rhel} < 7
(
  pushd mysql-%{compatver}
  mkdir build && pushd build
  %{cmake3} .. \
    -DBUILD_CONFIG=mysql_release \
    -DINSTALL_LAYOUT=RPM \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_C_FLAGS="%{optflags}" \
    -DCMAKE_CXX_FLAGS="%{optflags}" \
    -DWITH_INNODB_MEMCACHED=0 \
    -DINSTALL_LIBDIR="%{_lib}/mysql" \
    -DINSTALL_PLUGINDIR="%{_lib}/mysql/plugin" \
    -DINSTALL_SQLBENCHDIR=share \
    -DWITH_SYMVER16=1 \
    -DMYSQL_UNIX_ADDR="%{mysqldatadir}/mysql.sock" \
    -DFEATURE_SET="%{feature_set}" \
    -DWITH_EMBEDDED_SERVER=1 \
    -DWITH_EMBEDDED_SHARED_LIBRARY=1 \
    -DWITH_SSL=system \
    -DWITH_ZLIB=system \
    -DCOMPILATION_COMMENT="%{compilation_comment_release}" \
    -DCOMPILATION_COMMENT_SERVER="%{compilation_comment_server_release}" \
    -DMYSQL_SERVER_SUFFIX="%{?server_suffix}"
  echo BEGIN_NORMAL_CONFIG ; egrep '^#define' include/config.h ; echo END_NORMAL_CONFIG
  make %{?_smp_mflags} VERBOSE=1
  popd && popd
)
%endif # 0%{?rhel} < 7
%endif # 0%{?compatlib}

# Build debug versions of mysqld
mkdir debug
(
  cd debug
  # Attempt to remove any optimisation flags from the debug build
  optflags=$(echo "%{optflags}" | sed -e 's/-O2 / /' -e 's/-Wp,-D_FORTIFY_SOURCE=2/ /' -e 's/%{_lto_cflags}/ /')
  %{cmake3} ../%{src_dir} \
           -DBUILD_CONFIG=mysql_release \
           -DINSTALL_LAYOUT=RPM \
           -DCMAKE_BUILD_TYPE=Debug \
           -DWITH_BOOST=.. \
           -DCMAKE_C_FLAGS="$optflags" \
           -DCMAKE_CXX_FLAGS="$optflags" \
           -DUSE_LD_LLD=0 \
%if 0%{?ssl_default}
           -DWITH_AUTHENTICATION_CLIENT_PLUGINS=1 \
%else
           -DWITH_AUTHENTICATION_CLIENT_PLUGINS=0 \
           -DWITH_AUTHENTICATION_FIDO=0 \
           -DWITH_AUTHENTICATION_KERBEROS=0 \
           -DWITH_AUTHENTICATION_LDAP=0 \
           -DWITH_AUTHENTICATION_OCI=0 \
           -DWITH_COMPONENT_KEYRING_OCI=0 \
           -DWITH_CURL=0 \
           -DWITH_KEYRING_HASHICORP=0 \
           -DWITH_KEYRING_OCI=0 \
%endif # ssl_default
           -DWITH_CURL=system \
%if 0%{?systemd}
           -DWITH_SYSTEMD=1 \
%endif
           -DWITH_ROUTER=%{with_router} \
%if 0%{?cluster}
           -DWITH_NDB=1 \
%endif
%if 0%{?ndb_nodejs_path:1}
           -DNDB_NODEJS_PATH=%{ndb_nodejs_path} \
%endif
%if 0%{?ndb_nodejs_extras_path:1}
           -DNDB_NODEJS_EXTRAS_PATH=%{ndb_nodejs_extras_path} \
%endif
%if 0%{?commercial}
           -DWITH_MEB=%{with_meb} \
           %{?aws_sdk_option} \
%endif
           %{?ssl_option} \
           %{?mini_debug_option} \
           -DWITH_INNODB_MEMCACHED=1 \
           -DMYSQL_UNIX_ADDR="%{mysqldatadir}/mysql.sock" \
           -DMYSQLX_UNIX_ADDR="/var/run/mysqld/mysqlx.sock" \
           -DWITH_NUMA=1 \
           %{?mecab_option} \
           -DCOMPILATION_COMMENT="%{compilation_comment_debug}" \
           -DCOMPILATION_COMMENT_SERVER="%{compilation_comment_server_debug}" \
           -DMYSQL_SERVER_SUFFIX="%{?server_suffix}"
  echo BEGIN_DEBUG_CONFIG ; egrep '^#define' include/config.h ; echo END_DEBUG_CONFIG
  make %{?_smp_mflags} VERBOSE=1
)

# Build full release
mkdir release
(
  cd release
  %{cmake3} ../%{src_dir} \
           -DBUILD_CONFIG=mysql_release \
           -DINSTALL_LAYOUT=RPM \
           -DCMAKE_BUILD_TYPE=RelWithDebInfo \
	   -DWITH_BOOST=.. \
           -DCMAKE_C_FLAGS="%{optflags}" \
           -DCMAKE_CXX_FLAGS="%{optflags}" \
           -DUSE_LD_LLD=0 \
%if 0%{?ssl_default}
           -DWITH_AUTHENTICATION_CLIENT_PLUGINS=1 \
%else
           -DWITH_AUTHENTICATION_CLIENT_PLUGINS=0 \
           -DWITH_AUTHENTICATION_FIDO=0 \
           -DWITH_AUTHENTICATION_KERBEROS=0 \
           -DWITH_AUTHENTICATION_LDAP=0 \
           -DWITH_AUTHENTICATION_OCI=0 \
           -DWITH_COMPONENT_KEYRING_OCI=0 \
           -DWITH_CURL=0 \
           -DWITH_KEYRING_HASHICORP=0 \
           -DWITH_KEYRING_OCI=0 \
%endif # ssl_default
           -DWITH_CURL=system \
%if 0%{?systemd}
           -DWITH_SYSTEMD=1 \
%endif
           -DWITH_ROUTER=%{with_router} \
%if 0%{?cluster}
           -DWITH_NDB=1 \
%endif
%if 0%{?ndb_nodejs_path:1}
           -DNDB_NODEJS_PATH=%{ndb_nodejs_path} \
%endif
%if 0%{?ndb_nodejs_extras_path:1}
           -DNDB_NODEJS_EXTRAS_PATH=%{ndb_nodejs_extras_path} \
%endif
%if 0%{?commercial}
           -DWITH_MEB=%{with_meb} \
           %{?aws_sdk_option} \
%endif
           %{?ssl_option} \
           %{?mini_debug_option} \
           -DWITH_INNODB_MEMCACHED=1 \
           -DMYSQL_UNIX_ADDR="%{mysqldatadir}/mysql.sock" \
           -DMYSQLX_UNIX_ADDR="/var/run/mysqld/mysqlx.sock" \
           -DWITH_NUMA=1 \
           %{?mecab_option} \
           -DCOMPILATION_COMMENT="%{compilation_comment_release}" \
           -DCOMPILATION_COMMENT_SERVER="%{compilation_comment_server_release}" \
           -DMYSQL_SERVER_SUFFIX="%{?server_suffix}"
  echo BEGIN_NORMAL_CONFIG ; egrep '^#define' include/config.h ; echo END_NORMAL_CONFIG
  make %{?_smp_mflags} VERBOSE=1
)

%install
# /usr/bin/strip is too old on el6
%if 0%{?rhel} == 6
export STRIP=/opt/rh/devtoolset-8/root/usr/bin/strip
%endif

%if 0%{?compatlib}
# Install compat libs
dirs="libmysql libmysql_r"
%{?el7:dirs="build/libmysql build/libmysqld build/sql/share"}
for dir in $dirs ; do
    pushd mysql-%{compatver}/$dir
    make DESTDIR=%{buildroot} install
    popd
done
rm -f %{buildroot}%{_libdir}/mysql/libmysqlclient{,_r}.{a,la,so}
%{?el7:rm -f %{buildroot}%{_libdir}/mysql/libmysqld.{a,la,so}}
%endif # 0%{?compatlib}

MBD=$RPM_BUILD_DIR/%{src_dir}

# Ensure that needed directories exists
install -d -m 0751 %{buildroot}/var/lib/mysql
install -d -m 0755 %{buildroot}/var/run/mysqld
install -d -m 0750 %{buildroot}/var/lib/mysql-files
install -d -m 0750 %{buildroot}/var/lib/mysql-keyring

%if 0%{?with_router}
# Router directories
install -d -m 0755 %{buildroot}/var/log/mysqlrouter
install -d -m 0755 %{buildroot}/var/run/mysqlrouter
%endif

# Install all binaries
cd $MBD/release
make DESTDIR=%{buildroot} install

# Install config and logrotate
install -D -m 0644 packaging/rpm-common/mysql.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/mysql
install -D -m 0644 packaging/rpm-common/my.cnf %{buildroot}%{_sysconfdir}/my.cnf
install -d %{buildroot}%{_sysconfdir}/my.cnf.d
%if 0%{?systemd}
%else
install -D -m 0755 packaging/rpm-oel/mysql.init %{buildroot}%{_sysconfdir}/init.d/mysqld
%endif # systemd

# Add libdir to linker
install -d -m 0755 %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/mysql" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/mysql-%{_arch}.conf

# multiarch support
%ifarch %{multiarchs}
mv %{buildroot}/%{_bindir}/mysql_config %{buildroot}/%{_bindir}/mysql_config-%{__isa_bits}
install -p -m 0755 packaging/rpm-common/mysql_config.sh %{buildroot}/%{_bindir}/mysql_config
%endif

%if 0%{?with_router}
%if 0%{?systemd}
%else
install -D -p -m 0755 packaging/rpm-common/mysqlrouter.init %{buildroot}%{_sysconfdir}/init.d/mysqlrouter
%endif # systemd
install -D -p -m 0644 packaging/rpm-common/mysqlrouter.conf %{buildroot}%{_sysconfdir}/mysqlrouter/mysqlrouter.conf
%endif # with_router

# Remove files pages we explicitly do not want to package
rm -f %{buildroot}%{_datadir}/mysql-*/win_install_firewall.sql
rm -f %{buildroot}%{_datadir}/mysql-*/audit_log_filter_win_install.sql

%check
%if 0%{?runselftest} || 0%{?with_unittests}
pushd release
export CTEST_OUTPUT_ON_FAILURE=1
make test || true
%endif
%if 0%{?runselftest}
export MTR_BUILD_THREAD=auto
pushd mysql-test
./mtr \
    --mem --parallel=auto --force --retry=0 \
    --mysqld=--binlog-format=row \
    --suite-timeout=720 --testcase-timeout=30 \
    --clean-vardir
rm -r $(readlink var) var
%endif # runselftest

%pre server
/usr/sbin/groupadd -g 27 -o -r mysql >/dev/null 2>&1 || :
/usr/sbin/useradd -M -N -g mysql -o -r -d /var/lib/mysql -s /bin/false \
    -c "MySQL Server" -u 27 mysql >/dev/null 2>&1 || :

%post server
[ -e /var/log/mysqld.log ] || install -m0640 -omysql -gmysql /dev/null /var/log/mysqld.log >/dev/null 2>&1 || :
%if 0%{?systemd}
%systemd_post mysqld.service
/usr/bin/systemctl enable mysqld >/dev/null 2>&1 || :
%else
/sbin/chkconfig --add mysqld
%endif # systemd

%preun server
%if 0%{?systemd}
%systemd_preun mysqld.service
%else
if [ "$1" = 0 ]; then
    /sbin/service mysqld stop >/dev/null 2>&1 || :
    /sbin/chkconfig --del mysqld
fi
%endif

%postun server
%if 0%{?systemd}
%systemd_postun_with_restart mysqld.service
%else
if [ $1 -ge 1 ]; then
    /sbin/service mysqld condrestart >/dev/null 2>&1 || :
fi
%endif

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%if 0%{?compatlib}
%post libs-compat -p /sbin/ldconfig

%postun libs-compat -p /sbin/ldconfig
%endif

%{?el7:%postun embedded-compat -p /sbin/ldconfig}

%if 0%{?with_router}
%pre -n mysql-router-%{product_suffix}
/usr/sbin/groupadd -r mysqlrouter >/dev/null 2>&1 || :
/usr/sbin/useradd -M -N -g mysqlrouter -r -d /var/lib/mysqlrouter -s /bin/false \
    -c "MySQL Router" mysqlrouter >/dev/null 2>&1 || :

%post -n mysql-router-%{product_suffix}
/sbin/ldconfig
%if 0%{?systemd}
%systemd_post mysqlrouter.service
%else
/sbin/chkconfig --add mysqlrouter
%endif # systemd

%preun -n mysql-router-%{product_suffix}
%if 0%{?systemd}
%systemd_preun mysqlrouter.service
%else
if [ "$1" = 0 ]; then
    /sbin/service mysqlrouter stop >/dev/null 2>&1 || :
    /sbin/chkconfig --del mysqlrouter
fi
%endif # systemd

%postun -n mysql-router-%{product_suffix}
/sbin/ldconfig
%if 0%{?systemd}
%systemd_postun_with_restart mysqlrouter.service
%else
if [ $1 -ge 1 ]; then
    /sbin/service mysqlrouter condrestart >/dev/null 2>&1 || :
fi
%endif # systemd
%endif # with_router

%files server
%defattr(-, root, root, -)
%doc %{?license_files_server}
%doc %{src_dir}/Docs/INFO_SRC*
%doc release/Docs/INFO_BIN*
%attr(644, root, root) %{_mandir}/man1/innochecksum.1*
%attr(644, root, root) %{_mandir}/man1/ibd2sdi.1*
%attr(644, root, root) %{_mandir}/man1/my_print_defaults.1*
%attr(644, root, root) %{_mandir}/man1/myisam_ftdump.1*
%attr(644, root, root) %{_mandir}/man1/myisamchk.1*
%attr(644, root, root) %{_mandir}/man1/myisamlog.1*
%attr(644, root, root) %{_mandir}/man1/myisampack.1*
%attr(644, root, root) %{_mandir}/man8/mysqld.8*
%if 0%{?systemd}
%else
%attr(644, root, root) %{_mandir}/man1/mysqld_multi.1*
%attr(644, root, root) %{_mandir}/man1/mysqld_safe.1*
%exclude %attr(644, root, root) %{_mandir}/man1/mysql.server.1*
%endif # systemd
%attr(644, root, root) %{_mandir}/man1/mysqldumpslow.1*
%attr(644, root, root) %{_mandir}/man1/mysql_secure_installation.1*
%attr(644, root, root) %{_mandir}/man1/mysql_upgrade.1*
%attr(644, root, root) %{_mandir}/man1/mysqlman.1*
%attr(644, root, root) %{_mandir}/man1/mysql_tzinfo_to_sql.1*
%attr(644, root, root) %{_mandir}/man1/perror.1*
%attr(644, root, root) %{_mandir}/man1/mysql_ssl_rsa_setup.1*
%attr(644, root, root) %{_mandir}/man1/lz4_decompress.1*
%attr(644, root, root) %{_mandir}/man1/zlib_decompress.1*

%config(noreplace) %{_sysconfdir}/my.cnf
%dir %{_sysconfdir}/my.cnf.d

%attr(755, root, root) %{_bindir}/innochecksum
%attr(755, root, root) %{_bindir}/ibd2sdi
%attr(755, root, root) %{_bindir}/my_print_defaults
%attr(755, root, root) %{_bindir}/myisam_ftdump
%attr(755, root, root) %{_bindir}/myisamchk
%attr(755, root, root) %{_bindir}/myisamlog
%attr(755, root, root) %{_bindir}/myisampack
%attr(755, root, root) %{_bindir}/mysql_secure_installation
%attr(755, root, root) %{_bindir}/mysql_tzinfo_to_sql
%attr(755, root, root) %{_bindir}/mysql_upgrade
%attr(755, root, root) %{_bindir}/mysqldumpslow
%attr(755, root, root) %{_bindir}/perror
%attr(755, root, root) %{_bindir}/mysql_ssl_rsa_setup
%attr(755, root, root) %{_bindir}/lz4_decompress
%attr(755, root, root) %{_bindir}/zlib_decompress
%if 0%{?systemd}
%attr(755, root, root) %{_bindir}/mysqld_pre_systemd
%else
%attr(755, root, root) %{_bindir}/mysqld_multi
%attr(755, root, root) %{_bindir}/mysqld_safe
%exclude %{_datadir}/mysql-*/mysql.server
%exclude %{_datadir}/mysql-*/mysqld_multi.server
%endif # systemd
%attr(755, root, root) %{_sbindir}/mysqld

%dir %{_libdir}/mysql/private
%attr(755, root, root) %{_libdir}/mysql/private/libprotobuf-lite.so.3.19.4
%attr(755, root, root) %{_libdir}/mysql/private/libprotobuf.so.3.19.4

%dir %{_libdir}/mysql/plugin
%attr(755, root, root) %{_libdir}/mysql/plugin/adt_null.so
%attr(755, root, root) %{_libdir}/mysql/plugin/auth_socket.so
%attr(755, root, root) %{_libdir}/mysql/plugin/group_replication.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_log_sink_syseventlog.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_log_sink_json.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_log_filter_dragnet.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_mysqlbackup.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_validate_password.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_audit_api_message_emit.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_query_attributes.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_reference_cache.so
%attr(755, root, root) %{_libdir}/mysql/plugin/connection_control.so
%attr(755, root, root) %{_libdir}/mysql/plugin/ddl_rewriter.so
%attr(755, root, root) %{_libdir}/mysql/plugin/ha_example.so
%attr(755, root, root) %{_libdir}/mysql/plugin/ha_mock.so
%attr(755, root, root) %{_libdir}/mysql/plugin/keyring_file.so
%attr(755, root, root) %{_libdir}/mysql/plugin/keyring_udf.so
%attr(755, root, root) %{_libdir}/mysql/plugin/innodb_engine.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libmemcached.so
%attr(755, root, root) %{_libdir}/mysql/plugin/locking_service.so
%attr(755, root, root) %{_libdir}/mysql/plugin/mypluglib.so
%attr(755, root, root) %{_libdir}/mysql/plugin/mysql_clone.so
%attr(755, root, root) %{_libdir}/mysql/plugin/mysql_no_login.so
%attr(755, root, root) %{_libdir}/mysql/plugin/rewrite_example.so
%attr(755, root, root) %{_libdir}/mysql/plugin/rewriter.so
%attr(755, root, root) %{_libdir}/mysql/plugin/semisync_master.so
%attr(755, root, root) %{_libdir}/mysql/plugin/semisync_slave.so
%attr(755, root, root) %{_libdir}/mysql/plugin/semisync_source.so
%attr(755, root, root) %{_libdir}/mysql/plugin/semisync_replica.so
%attr(755, root, root) %{_libdir}/mysql/plugin/validate_password.so
%attr(755, root, root) %{_libdir}/mysql/plugin/version_token.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_keyring_file.so

%if 0%{?mecab}
%{_libdir}/mysql/mecab
%attr(755, root, root) %{_libdir}/mysql/plugin/libpluginmecab.so
%endif # mecab

%if 0%{?commercial}
%attr(755, root, root) %{_libdir}/mysql/plugin/audit_log.so
%attr(644, root, root) %{_datadir}/mysql-*/audit_log_filter_linux_install.sql
%attr(644, root, root) %{_datadir}/mysql-*/audit_log_filter_uninstall.sql
%attr(755, root, root) %{_libdir}/mysql/plugin/authentication_pam.so
%if 0%{?ssl_default}
%if 0%{?add_fido_plugins}
%attr(755, root, root) %{_libdir}/mysql/plugin/authentication_fido.so
%endif # add_fido_plugins
%attr(755, root, root) %{_libdir}/mysql/plugin/authentication_kerberos.so
%attr(755, root, root) %{_libdir}/mysql/plugin/authentication_ldap_sasl.so
%attr(755, root, root) %{_libdir}/mysql/plugin/authentication_ldap_simple.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_keyring_oci.so
%attr(755, root, root) %{_libdir}/mysql/plugin/keyring_hashicorp.so
%attr(755, root, root) %{_libdir}/mysql/plugin/keyring_oci.so
%endif # ssl_default
%attr(755, root, root) %{_libdir}/mysql/plugin/data_masking.so
%attr(755, root, root) %{_libdir}/mysql/plugin/keyring_okv.so
%attr(755, root, root) %{_libdir}/mysql/plugin/keyring_encrypted_file.so
%attr(755, root, root) %{_libdir}/mysql/plugin/thread_pool.so
%attr(755, root, root) %{_libdir}/mysql/plugin/openssl_udf.so
%attr(755, root, root) %{_libdir}/mysql/plugin/firewall.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_keyring_encrypted_file.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_enterprise_encryption.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_masking.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_masking_functions.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_scheduler.so
%attr(644, root, root) %{_datadir}/mysql-*/linux_install_firewall.sql
%attr(644, root, root) %{_datadir}/mysql-*/firewall_profile_migration.sql
%attr(644, root, root) %{_datadir}/mysql-*/masking_functions_install.sql
%attr(644, root, root) %{_datadir}/mysql-*/masking_functions_uninstall.sql
%if 0%{?aws_sdk}
%attr(755, root, root) %{_libdir}/mysql/plugin/keyring_aws.so
%endif # aws_sdk
%endif # commercial

%attr(644, root, root) %{_datadir}/mysql-*/mysql-log-rotate
%attr(644, root, root) %{_datadir}/mysql-*/dictionary.txt
%attr(644, root, root) %{_datadir}/mysql-*/innodb_memcached_config.sql
%attr(644, root, root) %{_datadir}/mysql-*/install_rewriter.sql
%attr(644, root, root) %{_datadir}/mysql-*/uninstall_rewriter.sql
%if 0%{?systemd}
%attr(644, root, root) %{_unitdir}/mysqld.service
%attr(644, root, root) %{_unitdir}/mysqld@.service
%attr(644, root, root) %{_prefix}/lib/tmpfiles.d/mysql.conf
%else
%attr(755, root, root) %{_sysconfdir}/init.d/mysqld
%endif # systemd
%attr(644, root, root) %config(noreplace,missingok) %{_sysconfdir}/logrotate.d/mysql
%dir %attr(751, mysql, mysql) /var/lib/mysql
%dir %attr(755, mysql, mysql) /var/run/mysqld
%dir %attr(750, mysql, mysql) /var/lib/mysql-files
%dir %attr(750, mysql, mysql) /var/lib/mysql-keyring

%if 0%{?with_debuginfo}
%files server-debug
%doc %{?license_files_server}
%endif # with_debuginfo
%attr(755, root, root) %{_sbindir}/mysqld-debug
%dir %{_libdir}/mysql/plugin/debug
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/adt_null.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/auth_socket.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/group_replication.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_log_sink_syseventlog.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_log_sink_json.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_log_filter_dragnet.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_mysqlbackup.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_validate_password.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_audit_api_message_emit.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_query_attributes.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_reference_cache.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/connection_control.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/ddl_rewriter.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/ha_example.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/ha_mock.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/keyring_file.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/keyring_udf.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/innodb_engine.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libmemcached.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/locking_service.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/mypluglib.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/mysql_clone.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/mysql_no_login.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/rewrite_example.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/rewriter.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/semisync_master.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/semisync_slave.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/semisync_source.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/semisync_replica.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/validate_password.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/version_token.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_keyring_file.so

%if 0%{?mecab}
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libpluginmecab.so
%endif # mecab

%if 0%{?commercial}
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/audit_log.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/authentication_pam.so
%if 0%{?ssl_default}
%if 0%{?add_fido_plugins}
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/authentication_fido.so
%endif # add_fido_plugins
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/authentication_kerberos.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/authentication_ldap_sasl.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/authentication_ldap_simple.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_keyring_oci.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/keyring_hashicorp.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/keyring_oci.so
%endif # ssl_default
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/data_masking.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/keyring_okv.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/keyring_encrypted_file.so

%attr(755, root, root) %{_libdir}/mysql/plugin/debug/thread_pool.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/openssl_udf.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/firewall.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_keyring_encrypted_file.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_enterprise_encryption.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_masking.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_masking_functions.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_scheduler.so
%if 0%{?aws_sdk}
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/keyring_aws.so
%endif # aws_sdk
%endif # commercial

%files common
%defattr(-, root, root, -)
%doc %{?license_files_server}
%{_datadir}/mysql-*/charsets/
%{_datadir}/mysql-*/messages_to_error_log.txt
%{_datadir}/mysql-*/messages_to_clients.txt
%{_datadir}/mysql-*/bulgarian/
%{_datadir}/mysql-*/czech/
%{_datadir}/mysql-*/danish/
%{_datadir}/mysql-*/dutch/
%{_datadir}/mysql-*/english/
%{_datadir}/mysql-*/estonian/
%{_datadir}/mysql-*/french/
%{_datadir}/mysql-*/german/
%{_datadir}/mysql-*/greek/
%{_datadir}/mysql-*/hungarian/
%{_datadir}/mysql-*/italian/
%{_datadir}/mysql-*/japanese/
%{_datadir}/mysql-*/korean/
%{_datadir}/mysql-*/norwegian-ny/
%{_datadir}/mysql-*/norwegian/
%{_datadir}/mysql-*/polish/
%{_datadir}/mysql-*/portuguese/
%{_datadir}/mysql-*/romanian/
%{_datadir}/mysql-*/russian/
%{_datadir}/mysql-*/serbian/
%{_datadir}/mysql-*/slovak/
%{_datadir}/mysql-*/spanish/
%{_datadir}/mysql-*/swedish/
%{_datadir}/mysql-*/ukrainian/

%files icu-data-files
%defattr(-, root, root, -)
%doc %{?license_files_server}
%dir %attr(755, root, root) %{_libdir}/mysql/private/icudt73l
%{_libdir}/mysql/private/icudt73l/cnvalias.icu
%{_libdir}/mysql/private/icudt73l/uemoji.icu
%{_libdir}/mysql/private/icudt73l/ulayout.icu
%{_libdir}/mysql/private/icudt73l/unames.icu
%{_libdir}/mysql/private/icudt73l/brkitr

%files client
%defattr(-, root, root, -)
%doc %{?license_files_server}
%attr(755, root, root) %{_bindir}/mysql
%attr(755, root, root) %{_bindir}/mysqladmin
%attr(755, root, root) %{_bindir}/mysqlbinlog
%attr(755, root, root) %{_bindir}/mysqlcheck
%attr(755, root, root) %{_bindir}/mysqldump
%attr(755, root, root) %{_bindir}/mysqlimport
%attr(755, root, root) %{_bindir}/mysqlpump
%attr(755, root, root) %{_bindir}/mysqlshow
%attr(755, root, root) %{_bindir}/mysqlslap
%attr(755, root, root) %{_bindir}/mysql_config_editor
%attr(755, root, root) %{_bindir}/mysql_migrate_keyring

%attr(644, root, root) %{_mandir}/man1/mysql.1*
%attr(644, root, root) %{_mandir}/man1/mysqladmin.1*
%attr(644, root, root) %{_mandir}/man1/mysqlbinlog.1*
%attr(644, root, root) %{_mandir}/man1/mysqlcheck.1*
%attr(644, root, root) %{_mandir}/man1/mysqldump.1*
%attr(644, root, root) %{_mandir}/man1/mysqlpump.1*
%attr(644, root, root) %{_mandir}/man1/mysqlimport.1*
%attr(644, root, root) %{_mandir}/man1/mysqlshow.1*
%attr(644, root, root) %{_mandir}/man1/mysqlslap.1*
%attr(644, root, root) %{_mandir}/man1/mysql_config_editor.1*


%if 0%{?cluster}
%attr(755, root, root) %{_bindir}/ndb_blob_tool
%attr(755, root, root) %{_bindir}/ndb_config
%attr(755, root, root) %{_bindir}/ndb_delete_all
%attr(755, root, root) %{_bindir}/ndb_desc
%attr(755, root, root) %{_bindir}/ndb_drop_index
%attr(755, root, root) %{_bindir}/ndb_drop_table
%attr(755, root, root) %{_bindir}/ndb_error_reporter
%attr(755, root, root) %{_bindir}/ndb_index_stat
%attr(755, root, root) %{_bindir}/ndb_import
%attr(755, root, root) %{_bindir}/ndb_mgm
%attr(755, root, root) %{_bindir}/ndb_move_data
%attr(755, root, root) %{_bindir}/ndb_perror
%attr(755, root, root) %{_bindir}/ndb_print_backup_file
%attr(755, root, root) %{_bindir}/ndb_print_file
%attr(755, root, root) %{_bindir}/ndb_print_frag_file
%attr(755, root, root) %{_bindir}/ndb_print_schema_file
%attr(755, root, root) %{_bindir}/ndb_print_sys_file
%attr(755, root, root) %{_bindir}/ndb_redo_log_reader
%attr(755, root, root) %{_bindir}/ndb_restore
%attr(755, root, root) %{_bindir}/ndb_secretsfile_reader
%attr(755, root, root) %{_bindir}/ndb_select_all
%attr(755, root, root) %{_bindir}/ndb_select_count
%attr(755, root, root) %{_bindir}/ndb_show_tables
%attr(755, root, root) %{_bindir}/ndb_size.pl
%attr(755, root, root) %{_bindir}/ndb_top
%attr(755, root, root) %{_bindir}/ndb_waiter
%attr(755, root, root) %{_bindir}/ndbinfo_select_all
%attr(755, root, root) %{_bindir}/ndbxfrm

%attr(644, root, root) %{_mandir}/man1/ndb_blob_tool.1*
%attr(644, root, root) %{_mandir}/man1/ndb_config.1*
%attr(644, root, root) %{_mandir}/man1/ndb_cpcd.1*
%attr(644, root, root) %{_mandir}/man1/ndb_delete_all.1*
%attr(644, root, root) %{_mandir}/man1/ndb_desc.1*
%attr(644, root, root) %{_mandir}/man1/ndb_drop_index.1*
%attr(644, root, root) %{_mandir}/man1/ndb_drop_table.1*
%attr(644, root, root) %{_mandir}/man1/ndb_error_reporter.1*
%attr(644, root, root) %{_mandir}/man1/ndb_import.1*
%attr(644, root, root) %{_mandir}/man1/ndb_index_stat.1*
%attr(644, root, root) %{_mandir}/man1/ndb_mgm.1*
%attr(644, root, root) %{_mandir}/man1/ndb_move_data.1*
%attr(644, root, root) %{_mandir}/man1/ndb_perror.1*
%attr(644, root, root) %{_mandir}/man1/ndb_print_backup_file.1*
%attr(644, root, root) %{_mandir}/man1/ndb_print_file.1*
%attr(644, root, root) %{_mandir}/man1/ndb_print_frag_file.1*
%attr(644, root, root) %{_mandir}/man1/ndb_print_schema_file.1*
%attr(644, root, root) %{_mandir}/man1/ndb_print_sys_file.1*
%attr(644, root, root) %{_mandir}/man1/ndb_redo_log_reader.1*
%attr(644, root, root) %{_mandir}/man1/ndb_restore.1*
%attr(644, root, root) %{_mandir}/man1/ndb_secretsfile_reader.1*
%attr(644, root, root) %{_mandir}/man1/ndb_select_all.1*
%attr(644, root, root) %{_mandir}/man1/ndb_select_count.1*
%attr(644, root, root) %{_mandir}/man1/ndb_show_tables.1*
%attr(644, root, root) %{_mandir}/man1/ndb_size.pl.1*
%attr(644, root, root) %{_mandir}/man1/ndb_top.1*
%attr(644, root, root) %{_mandir}/man1/ndb_waiter.1*
%attr(644, root, root) %{_mandir}/man1/ndbinfo_select_all.1*
%attr(644, root, root) %{_mandir}/man1/ndbxfrm.1*
%endif #cluster

%files devel
%defattr(-, root, root, -)
%doc %{?license_files_server}
%attr(644, root, root) %{_mandir}/man1/mysql_config.1*
%attr(755, root, root) %{_bindir}/mysql_config
%ifarch %{multiarchs}
%attr(755, root, root) %{_bindir}/mysql_config-%{__isa_bits}
%endif
%{_includedir}/mysql
%if 0%{?cluster}
%exclude %{_includedir}/mysql/storage
%endif #cluster
%{_datadir}/aclocal/mysql.m4
%{_libdir}/mysql/libmysqlclient.a
%{_libdir}/mysql/libmysqlservices.a
%{_libdir}/mysql/libmysqlclient.so
%{_libdir}/pkgconfig/mysqlclient.pc

%files libs
%defattr(-, root, root, -)
%doc %{?license_files_server}
%dir %attr(755, root, root) %{_libdir}/mysql
%attr(644, root, root) %{_sysconfdir}/ld.so.conf.d/mysql-%{_arch}.conf
%{_libdir}/mysql/libmysqlclient.so.21*
%if 0%{?ssl_bundled}
%attr(755, root, root) %{_libdir}/mysql/private/libssl.so
%attr(755, root, root) %{_libdir}/mysql/private/libssl.so.1.1
%attr(755, root, root) %{_libdir}/mysql/private/libcrypto.so
%attr(755, root, root) %{_libdir}/mysql/private/libcrypto.so.1.1
%endif # ssl_bundled

%files client-plugins
%defattr(-, root, root, -)
%doc %{?license_files_server}
%if 0%{?ssl_default}
%if 0%{?add_fido_plugins}
%attr(755, root, root) %{_libdir}/mysql/plugin/authentication_fido_client.so
%attr(755, root, root) %{_libdir}/mysql/private/libfido2.so.1
%attr(755, root, root) %{_libdir}/mysql/private/libfido2.so.1.13.0
%endif # add_fido_plugins
%attr(755, root, root) %{_libdir}/mysql/plugin/authentication_kerberos_client.so
%attr(755, root, root) %{_libdir}/mysql/plugin/authentication_ldap_sasl_client.so
%attr(755, root, root) %{_libdir}/mysql/plugin/authentication_oci_client.so
%endif # ssl_default

%if 0%{?compatlib}
%files libs-compat
%defattr(-, root, root, -)
%doc %{?license_files_server}
%dir %attr(755, root, root) %{_libdir}/mysql
%attr(644, root, root) %{_sysconfdir}/ld.so.conf.d/mysql-%{_arch}.conf
%{_libdir}/mysql/libmysqlclient.so.%{compatlib}
%{_libdir}/mysql/libmysqlclient.so.%{compatlib}.*.0
%{_libdir}/mysql/libmysqlclient_r.so.%{compatlib}
%{_libdir}/mysql/libmysqlclient_r.so.%{compatlib}.*.0
%endif

%files test
%defattr(-, root, root, -)
%doc %{?license_files_server}
%attr(-, root, root) %{_datadir}/mysql-test
%if 0%{?ssl_bundled}
%attr(755, root, root) %{_bindir}/my_openssl
%endif # ssl_bundled
%attr(755, root, root) %{_bindir}/comp_err
%attr(755, root, root) %{_bindir}/mysql_client_test
%attr(755, root, root) %{_bindir}/mysql_keyring_encryption_test
%if 0%{?systemd}
%attr(755, root, root) %{_bindir}/mysqld_safe
%endif
%attr(755, root, root) %{_bindir}/mysqltest
%attr(755, root, root) %{_bindir}/mysqltest_safe_process
%attr(755, root, root) %{_bindir}/mysqlxtest
%attr(644, root, root) %{_mandir}/man1/comp_err.1*

%attr(755, root, root) %{_libdir}/mysql/plugin/auth.so
%attr(755, root, root) %{_libdir}/mysql/plugin/auth_test_plugin.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_example_component1.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_example_component2.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_example_component3.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_log_sink_test.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_backup_lock_service.so
%if 0%{?commercial}
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_page_track_component.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_global_priv_registration.so
%endif
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_string_service_charset.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_string_service_long.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_string_service.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_pfs_example.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_pfs_example_component_population.so
%attr(755, root, root) %{_libdir}/mysql/plugin/pfs_example_plugin_employee.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_pfs_notification.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_pfs_resource_group.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_udf_registration.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_host_application_signal.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_mysql_current_thread_reader.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_mysql_runtime_error.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_mysql_system_variable_set.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_table_access.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_component_deinit.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_mysql_command_services.so
%attr(755, root, root) %{_libdir}/mysql/plugin/test_services_command_services.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_udf_reg_3_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_udf_reg_avg_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_udf_reg_int_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_udf_reg_int_same_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_udf_reg_only_3_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_udf_reg_real_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_udf_unreg_3_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_udf_unreg_int_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_udf_unreg_real_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_sys_var_service_int.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_sys_var_service.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_sys_var_service_same.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_sys_var_service_str.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_status_var_service.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_status_var_service_int.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_status_var_service_reg_only.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_status_var_service_str.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_status_var_service_unreg_only.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_system_variable_source.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_audit_api_message.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_udf_services.so
%attr(755, root, root) %{_libdir}/mysql/plugin/conflicting_variables.so
%attr(644, root, root) %{_libdir}/mysql/plugin/daemon_example.ini
%attr(755, root, root) %{_libdir}/mysql/plugin/libdaemon_example.so
%attr(755, root, root) %{_libdir}/mysql/plugin/replication_observers_example_plugin.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_framework.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_services.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_services_threaded.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_session_detach.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_session_attach.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_session_in_thd.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_session_info.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_2_sessions.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_all_col_types.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_cmds_1.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_commit.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_complex.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_errors.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_lock.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_processlist.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_replication.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_shutdown.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_sleep_is_connected.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_stmt.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_sqlmode.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_stored_procedures_functions.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_views_triggers.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_sql_reset_connection.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_x_sessions_deinit.so
%attr(755, root, root) %{_libdir}/mysql/plugin/libtest_x_sessions_init.so
%attr(755, root, root) %{_libdir}/mysql/plugin/qa_auth_client.so
%attr(755, root, root) %{_libdir}/mysql/plugin/qa_auth_interface.so
%attr(755, root, root) %{_libdir}/mysql/plugin/qa_auth_server.so
%attr(755, root, root) %{_libdir}/mysql/plugin/test_security_context.so
%attr(755, root, root) %{_libdir}/mysql/plugin/test_services_plugin_registry.so
%attr(755, root, root) %{_libdir}/mysql/plugin/test_services_host_application_signal.so
%attr(755, root, root) %{_libdir}/mysql/plugin/test_udf_services.so
%attr(755, root, root) %{_libdir}/mysql/plugin/udf_example.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_mysqlx_global_reset.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_sensitive_system_variables.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_status_var_reader.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_server_telemetry_traces.so
%attr(755, root, root) %{_libdir}/mysql/plugin/component_test_mysql_thd_store_service.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/auth.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/auth_test_plugin.so
%if 0%{?ssl_default}
%if 0%{?add_fido_plugins}
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/authentication_fido_client.so
%endif # add_fido_plugins
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/authentication_kerberos_client.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/authentication_ldap_sasl_client.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/authentication_oci_client.so
%endif # ssl_default
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_example_component1.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_example_component2.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_example_component3.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_log_sink_test.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_backup_lock_service.so
%if 0%{?commercial}
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_page_track_component.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_global_priv_registration.so
%endif
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_string_service_charset.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_string_service_long.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_string_service.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_pfs_example.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_pfs_example_component_population.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/pfs_example_plugin_employee.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_pfs_notification.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_pfs_resource_group.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_udf_registration.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_host_application_signal.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_mysql_current_thread_reader.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_mysql_runtime_error.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_mysql_system_variable_set.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_table_access.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_component_deinit.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_mysql_command_services.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/test_services_command_services.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_udf_reg_3_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_udf_reg_avg_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_udf_reg_int_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_udf_reg_int_same_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_udf_reg_only_3_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_udf_reg_real_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_udf_unreg_3_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_udf_unreg_int_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_udf_unreg_real_func.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_sys_var_service_int.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_sys_var_service.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_sys_var_service_same.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_sys_var_service_str.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_status_var_service.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_status_var_service_int.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_status_var_service_reg_only.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_status_var_service_str.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_status_var_service_unreg_only.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_system_variable_source.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_audit_api_message.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_udf_services.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/conflicting_variables.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libdaemon_example.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/replication_observers_example_plugin.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_framework.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_services.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_services_threaded.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_session_detach.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_session_attach.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_session_in_thd.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_session_info.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_2_sessions.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_all_col_types.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_cmds_1.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_commit.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_complex.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_errors.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_lock.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_processlist.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_replication.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_shutdown.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_sleep_is_connected.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_stmt.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_sqlmode.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_stored_procedures_functions.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_views_triggers.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_sql_reset_connection.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_x_sessions_deinit.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/libtest_x_sessions_init.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/qa_auth_client.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/qa_auth_interface.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/qa_auth_server.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/test_security_context.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/test_services_plugin_registry.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/test_services_host_application_signal.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/test_udf_services.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/udf_example.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_mysqlx_global_reset.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_sensitive_system_variables.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_status_var_reader.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_server_telemetry_traces.so
%attr(755, root, root) %{_libdir}/mysql/plugin/debug/component_test_mysql_thd_store_service.so

%if 0%{?rhel} == 7
%files embedded-compat
%defattr(-, root, root, -)
%doc %{?license_files_server}
%dir %attr(755, root, root) %{_libdir}/mysql
%attr(644, root, root) %{_sysconfdir}/ld.so.conf.d/mysql-%{_arch}.conf
%attr(755, root, root) %{_libdir}/mysql/libmysqld.so.18*
%{_datadir}/mysql/charsets/
%{_datadir}/mysql/errmsg-utf8.txt
%{_datadir}/mysql/bulgarian/
%{_datadir}/mysql/czech/
%{_datadir}/mysql/danish/
%{_datadir}/mysql/dutch/
%{_datadir}/mysql/english/
%{_datadir}/mysql/estonian/
%{_datadir}/mysql/french/
%{_datadir}/mysql/german/
%{_datadir}/mysql/greek/
%{_datadir}/mysql/hungarian/
%{_datadir}/mysql/italian/
%{_datadir}/mysql/japanese/
%{_datadir}/mysql/korean/
%{_datadir}/mysql/norwegian-ny/
%{_datadir}/mysql/norwegian/
%{_datadir}/mysql/polish/
%{_datadir}/mysql/portuguese/
%{_datadir}/mysql/romanian/
%{_datadir}/mysql/russian/
%{_datadir}/mysql/serbian/
%{_datadir}/mysql/slovak/
%{_datadir}/mysql/spanish/
%{_datadir}/mysql/swedish/
%{_datadir}/mysql/ukrainian/
%exclude %{_datadir}/mysql/dictionary.txt
%endif

%if 0%{?cluster}
%files management-server
%defattr(-, root, root, -)
%doc %{?license_files_server}
%attr(755, root, root) %{_sbindir}/ndb_mgmd
%attr(644, root, root) %{_mandir}/man8/ndb_mgmd.8*

%files data-node
%defattr(-, root, root, -)
%doc %{?license_files_server}
%attr(755, root, root) %{_sbindir}/ndbd
%attr(755, root, root) %{_sbindir}/ndbmtd
%attr(644, root, root) %{_mandir}/man8/ndbd.8*
%attr(644, root, root) %{_mandir}/man8/ndbmtd.8*

%files ndbclient
%defattr(-, root, root, -)
%doc %{?license_files_server}
%attr(755, root, root) %{_libdir}/mysql/libndbclient.so.6.1.0

%files ndbclient-devel
%defattr(-, root, root, -)
%doc %{?license_files_server}
%attr(644, root, root) %{_libdir}/mysql/libndbclient_static.a
%{_libdir}/mysql/libndbclient.so
%{_includedir}/mysql/storage

%if 0%{?ndb_nodejs_extras_path:1}
%files nodejs
%defattr(-, root, root, -)
%doc %{?license_files_server}
%{_datadir}/mysql-*/nodejs/
%endif

%files java
%defattr(-, root, root, -)
%doc %{?license_files_server}
%{_datadir}/mysql-*/java/
%endif # cluster

%if 0%{?with_meb}
%files backup
%defattr(-, root, root, -)
%doc %{src_dir}/packaging/meb/LICENSE.meb
%doc %{src_dir}/packaging/meb/README.meb
%doc %{src_dir}/Docs/INFO_SRC*
%doc release/Docs/INFO_BIN*
%attr(755, root, root) %{_bindir}/mysqlbackup
%endif # with_meb

%if 0%{?with_router}
%files -n mysql-router-%{product_suffix}
%defattr(-, root, root, -)
%doc %{src_dir}/router/README.router  %{src_dir}/router/LICENSE.router
%doc %{src_dir}/Docs/INFO_SRC*
%doc release/Docs/INFO_BIN*
%dir %{_sysconfdir}/mysqlrouter
%config(noreplace) %{_sysconfdir}/mysqlrouter/mysqlrouter.conf
%attr(644, root, root) %config(noreplace,missingok) %{_sysconfdir}/logrotate.d/mysqlrouter
%{_bindir}/mysqlrouter
%{_bindir}/mysqlrouter_keyring
%{_bindir}/mysqlrouter_passwd
%{_bindir}/mysqlrouter_plugin_info
%attr(644, root, root) %{_mandir}/man1/mysqlrouter.1*
%attr(644, root, root) %{_mandir}/man1/mysqlrouter_passwd.1*
%attr(644, root, root) %{_mandir}/man1/mysqlrouter_plugin_info.1*
%if 0%{?systemd}
%{_unitdir}/mysqlrouter.service
%{_tmpfilesdir}/mysqlrouter.conf
%else
%{_sysconfdir}/init.d/mysqlrouter
%endif
%{_libdir}/mysqlrouter/private/libmysqlharness.so.*
%{_libdir}/mysqlrouter/private/libmysqlharness_stdx.so.*
%{_libdir}/mysqlrouter/private/libmysqlharness_tls.so.*
%{_libdir}/mysqlrouter/private/libmysqlrouter.so.*
%{_libdir}/mysqlrouter/private/libmysqlrouter_connection_pool.so.*
%{_libdir}/mysqlrouter/private/libmysqlrouter_destination_status.so.*
%{_libdir}/mysqlrouter/private/libmysqlrouter_http.so.*
%{_libdir}/mysqlrouter/private/libmysqlrouter_http_auth_backend.so.*
%{_libdir}/mysqlrouter/private/libmysqlrouter_http_auth_realm.so.*
%{_libdir}/mysqlrouter/private/libmysqlrouter_io_component.so.*
%{_libdir}/mysqlrouter/private/libmysqlrouter_metadata_cache.so.*
%{_libdir}/mysqlrouter/private/libmysqlrouter_mysqlxmessages.so.*
%{_libdir}/mysqlrouter/private/libmysqlrouter_routing.so.*
%{_libdir}/mysqlrouter/private/libprotobuf-lite.so.3.19.4
%dir %{_libdir}/mysqlrouter
%dir %{_libdir}/mysqlrouter/private
%{_libdir}/mysqlrouter/*.so
%dir %attr(755, mysqlrouter, mysqlrouter) /var/log/mysqlrouter
%dir %attr(755, mysqlrouter, mysqlrouter) /var/run/mysqlrouter
%endif # with_router

%changelog
* Thu Oct 13 2022 Miroslav Rajcic <miroslav.rajcic@oracle.com> - 8.0.33-1
- Added component_test_server_telemetry_traces, component_test_mysql_thd_store_service

* Tue Oct 11 2022 Michal Jankowski <michal.jankowski@oracle.com> - 8.0.33-1
- Added component_masking.so component
- Added component_masking_functions.so component

* Tue Jun 28 2022 Samar Pratap Singh <samar.pratap.singh@oracle.com> - 8.0.31-1
- Added component_keyring_oci

* Mon Jun 20 2022 Murthy Sidagam <venkata.sidagam@oracle.com> - 8.0.31-1
- Added component_test_mysql_command_services.so test component
- Added test_services_command_services.so test plugin

* Wed Feb 02 2022 Harin Vadodaria <harin.vadodaria@oracle.com> - 8.0.30-1
- Added component_enterprise_encryption

* Mon Jan 03 2022 Harin Vadodaria <harin.vadodaria@oracle.com> - 8.0.29-1
- Added component_test_sensitive_system_variables

* Tue Aug 31 2021 Harin Vadodaria <harin.vadodaria@oracle.com> - 8.0.27-1
- Added authentication_oci_client

* Mon Sep 21 2020 Murthy Sidagam <venkata.sidagam@oracle.com> - 8.0.23-1
- Added component_reference_cache.so component

* Wed Sep 09 2020 Joro Kodinov <georgi.kodinov@oracle.com> - 8.0.23-1
- Add a new component_query_attributes

* Sun Jul 12 2020 Sreedhar S <sreedhar.sreedhargadda@oracle.com> - 8.0.22-1
- Add a new subpackage client-plugins
- Added component_keyring_file component
- Added component_keyring_encrypted_file component
- Added mysql_migrate_keyring

* Tue Feb 04 2020 Bjorn Munch <bjorn.munch@oracle.com> - 8.0.20-1
- Again add back support for alternative with_ssl, now with bundled openssl

* Wed Aug 14 2019 Rahul Sisondia <rahul.sisondia@oracle.com> - 8.0.19-1
- Added component_test_udf_services test component

* Fri Jun 28 2019 Ivan Svaljek <ivan.svaljek@oracle.com> - 8.0.18-1
- Add keyring_hashicorp.so plugin
- Add component_mysqlbackup component

* Mon May 13 2019 Bjorn Munch <bjorn.munch@oracle.com> - 8.0.17-1
- Add router man pages
- Bundle mecab as usual on el8
- Ship debuginfo and separate server-debug package on el8
- Some clean up

* Mon Feb 18 2019 Terje Rosten <terje.rosten@oracle.com> - 8.0.16-1
- Initial el8 packaging
- Add back support for alternative with_ssl

* Fri Dec 14 2018 Murthy Sidagam <venkata.sidagam@oracle.com> - 8.0.15-1
- Added component_test_mysql_runtime_error.so test component

* Wed Nov 21 2018 Erlend Dahl <erlend.dahl@oracle.com> - 8.0.14-1
- Add specific compilation comment for the server
- Remove resolveip
- Remove resolve_stack_dump

* Mon Aug 20 2018 Georgi Kodinov <georgi.kodinov@oracle.com> - 8.0.13-1
- Added test_services_host_application_signal test plugin
- Adapt to numbered share directory for NDB files
- Add Router

* Mon Mar 12 2018 Erlend Dahl <erlend.dahl@oracle.com> - 8.0.12-1
- Move mysqlx to default plugin
- Add component_mysqlx_global_reset.so
- Change the global milestone to 'dmr'
- Add meb as sub package
- Remove obsoleted mysqltest man pages
- Independently choose SSL for the 5.6 compat lib, depending on commercial
- Include udf_example.so in test package
- Add component_validate_password component
- Add License Book, remove COPYING
- No longer need to remove obsoleted mysqltest man pages
- Add perl modules for test subpackage
- Add router as subpackage

* Fri Jul 28 2017 Horst Hunger <horst.hunger@oracle.com> - 8.0.3-0.1
- Add component_test_status_var_service plugin

* Fri May 26 2017 Harin Vadodaria <harin.vadodaria@oracle.com> - 8.0.2-0.1
- Add keyring_aws plugin and UDF components
- Add component_test_sys_var_service plugins

* Tue Sep 13 2016 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 8.0.1-0.1
- Add test_services_plugin_registry.so plugin
- Add connection_control.so to server subpackage

* Tue Jul 05 2016 Erlend Dahl <erlend.dahl@oracle.com> - 8.0.0-0.1
- Change the version number to 8.0.0
- Add manual page for ibd2sdi utility
- Adapt MySQL server 5.7 packaging to MySQL Cluster 7.5
- Remove mysql_config from client subpackage

* Fri Jun 03 2016 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.8.0-0.1
- Updated compatver to 5.6.31
- Add example component to test package
- Add test_udf_services.so plugin
- Add keyring_udf.so plugin to server subpackage
- Add keyring_okv.so plugin to commercial server subpackage
- Purge man page for mysql_install_db in preparation for its removal
- Include mysql-keyring directory
- Provide keyring_file.so plugin

* Tue Nov 24 2015 Bjorn Munch <bjorn.munch@oracle.com> - 5.7.10-1
- Included man pages for lz4_decompress and zlib_decompress

* Thu Nov 12 2015 Bjorn Munch <bjorn.munch@oracle.com> - 5.7.10-1
- Added lines to remove man pages we are not ready to include yet
- Added lz4_decompress and zlib_decompress binaries to client subpackage
- Drop support for el5, use scl to build on el6

* Mon Oct 19 2015 Bharathy Satish <bharathy.x.satish@oracle.com> - 5.7.10-1
- Added new decompression utilities lz4_decompress and zlib_decompress binaries to
  client subpackage.

* Mon Oct 5 2015 Tor Didriksen <tor.didriksen@oracle.com>
- Added mysqlx.so

* Tue Sep 29 2015 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.9-1
- Updated for 5.7.9
- Added libtest_* plugins to test subpackage
- Add mysqlpump man page
- Obsolete mysql-connector-c-shared dependencies

* Mon Jul 06 2015 Murthy Narkedimilli <murthy.narkedimilli@oracle.com> - 5.7.8-0.2.rc
- Bumped the version of libmysqlclient.so and libmysqld.so from 20 -> 21.

* Thu Jun 25 2015 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.8-0.2.rc
- Add support for pkg-config

* Wed May 20 2015 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.8-0.2.rc
- Added libtest_framework.so, libtest_services.so, libtest_services_threaded.so plugins
- Build and ship mecab plugin

* Tue Feb 3 2015 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.6-0.2.m16
- Include boost sources
- Fix cmake buildrequires
- Fix build on el5 with gcc44
- Add license info in each subpackage
- Soname bump, more compat packages
- Updated default shell for mysql user
- Added mysql_ssl_rsa_setup
- Include mysql-files directory

* Thu Sep 18 2014 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.6-0.2.m16
- Provide replication_observers_example_plugin.so plugin

* Tue Sep 2 2014 Bjorn Munch <bjorn.munch@oracle.com> - 5.7.6-0.1.m16
- Updated for 5.7.6

* Fri Aug 08 2014 Erlend Dahl <erlend.dahl@oracle.com> - 5.7.5-0.6.m15
- Provide mysql_no_login.so plugin

* Wed Aug 06 2014 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.5-0.5.m15
- Provide mysql-compat-server dependencies 

* Wed Jul 09 2014 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.5-0.4.m15
- Remove perl(GD) and dtrace dependencies

* Thu Jun 26 2014 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.5-0.3.m15
- Resolve embedded-devel conflict issue

* Wed Jun 25 2014 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.5-0.2.m15
- Add bench package
- Enable dtrace 

* Thu Apr 24 2014 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.5-0.1.m15
- Updated for 5.7.5

* Mon Apr 07 2014 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.4-0.5.m14
- Fix Cflags for el7 

* Mon Mar 31 2014 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.4-0.4.m14
- Support for enterprise packages
- Upgrade from MySQL-* packages

* Wed Mar 12 2014 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.4-0.3.m14
- Resolve conflict with mysql-libs-compat 

* Thu Mar 06 2014 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.4-0.2.m14
- Resolve conflict issues during upgrade
- Add ha_example.so plugin which is now included

* Fri Feb 07 2014 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.4-0.1.m14
- 5.7.4
- Enable shared libmysqld by cmake option
- Move mysqltest and test plugins to test subpackage

* Mon Nov 18 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.3-0.3.m13
- Fixed isa_bits error 

* Fri Oct 25 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.7.3-0.1.m13
- Initial 5.7 port

* Fri Oct 25 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.15-1
- Fixed uln advanced rpm libyassl.a error
- Updated to 5.6.15

* Wed Oct 16 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.14-3
- Fixed mysql_install_db usage 
- Improved handling of plugin directory 

* Fri Sep 27 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.14-2
- Refresh mysql-install patch and service renaming

* Mon Sep 16 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.14-1
- Updated to 5.6.14

* Wed Sep 04 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.13-5
- Support upgrade from 5.5 ULN packages to 5.6 

* Tue Aug 27 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.13-4
- Enhanced perl filtering 
- Added openssl-devel to buildreq 

* Wed Aug 21 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.13-3
- Removed mysql_embedded binary to resolve multilib conflict issue

* Fri Aug 16 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.13-2 
- Fixed Provides and Obsoletes issues in server, test packages 

* Wed Aug 14 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.13-1
- Updated to 5.6.13

* Mon Aug 05 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.12-9
- Added files list to embedded packages 

* Thu Aug 01 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.12-8
- Updated libmysqld.a with libmysqld.so in embedded package

* Mon Jul 29 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.12-7
- Updated test package dependency from client to server

* Wed Jul 24 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.12-6
- Added libs-compat dependency under libs package to resolve server
  installation conflicts issue.
 
* Wed Jul 17 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.12-5
- Removed libmysqlclient.so.16 from libs package
 
* Fri Jul 05 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.12-4
- Adjusted to work on OEL6

* Wed Jun 26 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.12-3
- Move libs to mysql/
- Basic multi arch support
- Fix changelog dates

* Thu Jun 20 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.12-2
- Major cleanup

* Tue Jun 04 2013 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 5.6.12-1
- Updated to 5.6.12

* Mon Nov 05 2012 Joerg Bruehe <joerg.bruehe@oracle.com>

- Allow to override the default to use the bundled yaSSL by an option like
      --define="with_ssl /path/to/ssl"

* Wed Oct 10 2012 Bjorn Munch <bjorn.munch@oracle.com>

- Replace old my-*.cnf config file examples with template my-default.cnf

* Fri Oct 05 2012 Joerg Bruehe <joerg.bruehe@oracle.com>

- Let the installation use the new option "--random-passwords" of "mysql_install_db".
  (Bug# 12794345 Ensure root password)
- Fix an inconsistency: "new install" vs "upgrade" are told from the (non)existence
  of "$mysql_datadir/mysql" (holding table "mysql.user" and other system stuff).

* Tue Jul 24 2012 Joerg Bruehe <joerg.bruehe@oracle.com>

- Add a macro "runselftest":
  if set to 1 (default), the test suite will be run during the RPM build;
  this can be oveeridden via the command line by adding
      --define "runselftest 0"
  Failures of the test suite will NOT make the RPM build fail!

* Mon Jul 16 2012 Joerg Bruehe <joerg.bruehe@oracle.com>

- Add the man page for the "mysql_config_editor".

* Mon Jun 11 2012 Joerg Bruehe <joerg.bruehe@oracle.com>

- Make sure newly added "SPECIFIC-ULN/" directory does not disturb packaging.

* Wed Feb 29 2012 Brajmohan Saxena <brajmohan.saxena@oracle.com>

- Removal all traces of the readline library from mysql (BUG 13738013)

* Wed Sep 28 2011 Joerg Bruehe <joerg.bruehe@oracle.com>

- Fix duplicate mentioning of "mysql_plugin" and its manual page,
  it is better to keep alphabetic order in the files list (merging!).

* Wed Sep 14 2011 Joerg Bruehe <joerg.bruehe@oracle.com>

- Let the RPM capabilities ("obsoletes" etc) ensure that an upgrade may replace
  the RPMs of any configuration (of the current or the preceding release series)
  by the new ones. This is done by not using the implicitly generated capabilities
  (which include the configuration name) and relying on more generic ones which
  just list the function ("server", "client", ...).
  The implicit generation cannot be prevented, so all these capabilities must be
  explicitly listed in "Obsoletes:"

* Tue Sep 13 2011 Jonathan Perkin <jonathan.perkin@oracle.com>

- Add support for Oracle Linux 6 and Red Hat Enterprise Linux 6.  Due to
  changes in RPM behaviour ($RPM_BUILD_ROOT is removed prior to install)
  this necessitated a move of the libmygcc.a installation to the install
  phase, which is probably where it belonged in the first place.

* Tue Sep 13 2011 Joerg Bruehe <joerg.bruehe@oracle.com>

- "make_win_bin_dist" and its manual are dropped, cmake does it different.

* Thu Sep 08 2011 Daniel Fischer <daniel.fischer@oracle.com>

- Add mysql_plugin man page.

* Tue Aug 30 2011 Tor Didriksen <tor.didriksen@oracle.com>

- Set CXX=g++ by default to add a dependency on libgcc/libstdc++.
  Also, remove the use of the -fno-exceptions and -fno-rtti flags.
  TODO: update distro_buildreq/distro_requires

* Tue Aug 30 2011 Joerg Bruehe <joerg.bruehe@oracle.com>

- Add the manual page for "mysql_plugin" to the server package.

* Fri Aug 19 2011 Joerg Bruehe <joerg.bruehe@oracle.com>

- Null-upmerge the fix of bug#37165: This spec file is not affected.
- Replace "/var/lib/mysql" by the spec file variable "%%{mysqldatadir}".

* Fri Aug 12 2011 Daniel Fischer <daniel.fischer@oracle.com>

- Source plugin library files list from cmake-generated file.

* Mon Jul 25 2011 Chuck Bell <chuck.bell@oracle.com>

- Added the mysql_plugin client - enables or disables plugins.

* Thu Jul 21 2011 Sunanda Menon <sunanda.menon@oracle.com>

- Fix bug#12561297: Added the MySQL embedded binary

* Thu Jul 07 2011 Joerg Bruehe <joerg.bruehe@oracle.com>

- Fix bug#45415: "rpm upgrade recreates test database"
  Let the creation of the "test" database happen only during a new installation,
  not in an RPM upgrade.
  This affects both the "mkdir" and the call of "mysql_install_db".

* Wed Feb 09 2011 Joerg Bruehe <joerg.bruehe@oracle.com>

- Fix bug#56581: If an installation deviates from the default file locations
  ("datadir" and "pid-file"), the mechanism to detect a running server (on upgrade)
  should still work, and use these locations.
  The problem was that the fix for bug#27072 did not check for local settings.

* Mon Jan 31 2011 Joerg Bruehe <joerg.bruehe@oracle.com>

- Install the new "manifest" files: "INFO_SRC" and "INFO_BIN".

* Tue Nov 23 2010 Jonathan Perkin <jonathan.perkin@oracle.com>

- EXCEPTIONS-CLIENT has been deleted, remove it from here too
- Support MYSQL_BUILD_MAKE_JFLAG environment variable for passing
  a '-j' argument to make.

* Mon Nov 1 2010 Georgi Kodinov <georgi.godinov@oracle.com>

- Added test authentication (WL#1054) plugin binaries

* Wed Oct 6 2010 Georgi Kodinov <georgi.godinov@oracle.com>

- Added example external authentication (WL#1054) plugin binaries

* Wed Aug 11 2010 Joerg Bruehe <joerg.bruehe@oracle.com>

- With a recent spec file cleanup, names have changed: A "-community" part was dropped.
  Reflect that in the "Obsoletes" specifications.
- Add a "triggerpostun" to handle the uninstall of the "-community" server RPM.
- This fixes bug#55015 "MySQL server is not restarted properly after RPM upgrade".

* Tue Jun 15 2010 Joerg Bruehe <joerg.bruehe@sun.com>

- Change the behaviour on installation and upgrade:
  On installation, do not autostart the server.
  *Iff* the server was stopped before the upgrade is started, this is taken as a
  sign the administrator is handling that manually, and so the new server will
  not be started automatically at the end of the upgrade.
  The start/stop scripts will still be installed, so the server will be started
  on the next machine boot.
  This is the 5.5 version of fixing bug#27072 (RPM autostarting the server).

* Tue Jun 1 2010 Jonathan Perkin <jonathan.perkin@oracle.com>

- Implement SELinux checks from distribution-specific spec file.

* Wed May 12 2010 Jonathan Perkin <jonathan.perkin@oracle.com>

- Large number of changes to build using CMake
- Introduce distribution-specific RPMs
- Drop debuginfo, build all binaries with debug/symbols
- Remove __os_install_post, use native macro
- Remove _unpackaged_files_terminate_build, make it an error to have
  unpackaged files
- Remove cluster RPMs

* Wed Mar 24 2010 Joerg Bruehe <joerg.bruehe@sun.com>

- Add "--with-perfschema" to the configure options.

* Mon Mar 22 2010 Joerg Bruehe <joerg.bruehe@sun.com>

- User "usr/lib*" to allow for both "usr/lib" and "usr/lib64",
  mask "rmdir" return code 1.
- Remove "ha_example.*" files from the list, they aren't built.

* Wed Mar 17 2010 Joerg Bruehe <joerg.bruehe@sun.com>

- Fix a wrong path name in handling the debug plugins.

* Wed Mar 10 2010 Joerg Bruehe <joerg.bruehe@sun.com>

- Take the result of the debug plugin build and put it into the optimized tree,
  so that it becomes part of the final installation;
  include the files in the packlist. Part of the fixes for bug#49022.

* Mon Mar 01 2010 Joerg Bruehe <joerg.bruehe@sun.com>

- Set "Oracle and/or its affiliates" as the vendor and copyright owner,
  accept upgrading from packages showing MySQL or Sun as vendor.

* Fri Feb 12 2010 Joerg Bruehe <joerg.bruehe@sun.com>

- Formatting changes:
  Have a consistent structure of separator lines and of indentation
  (8 leading blanks => tab).
- Introduce the variable "src_dir".
- Give the environment variables "MYSQL_BUILD_CC(CXX)" precedence
  over "CC" ("CXX").
- Drop the old "with_static" argument analysis, this is not supported
  in 5.1 since ages.
- Introduce variables to control the handlers individually, as well
  as other options.
- Use the new "--with-plugin" notation for the table handlers.
- Drop handling "/etc/rc.d/init.d/mysql", the switch to "/etc/init.d/mysql"
  was done back in 2002 already.
- Make "--with-zlib-dir=bundled" the default, add an option to disable it.
- Add missing manual pages to the file list.
- Improve the runtime check for "libgcc.a", protect it against being tried
  with the Intel compiler "icc".

* Mon Jan 11 2010 Joerg Bruehe <joerg.bruehe@sun.com>

- Change RPM file naming:
  - Suffix like "-m2", "-rc" becomes part of version as "_m2", "_rc".
  - Release counts from 1, not 0.

* Wed Dec 23 2009 Joerg Bruehe <joerg.bruehe@sun.com>

- The "semisync" plugin file name has lost its introductory "lib",
  adapt the file lists for the subpackages.
  This is a part missing from the fix for bug#48351.
- Remove the "fix_privilege_tables" manual, it does not exist in 5.5
  (and likely, the whole script will go, too).

* Mon Nov 16 2009 Joerg Bruehe <joerg.bruehe@sun.com>

- remove erroneous traces of the InnoDB plugin (that is 5.1 only).

* Tue Oct 06 2009 Magnus Blaudd <mvensson@mysql.com>

- Removed mysql_fix_privilege_tables

* Fri Oct 02 2009 Alexander Nozdrin <alexander.nozdrin@sun.com>

- "mysqlmanager" got removed from version 5.4, all references deleted.

* Fri Aug 28 2009 Joerg Bruehe <joerg.bruehe@sun.com>

- Merge up from 5.1 to 5.4: Remove handling for the InnoDB plugin.

* Thu Aug 27 2009 Joerg Bruehe <joerg.bruehe@sun.com>

- This version does not contain the "Instance manager", "mysqlmanager":
  Remove it from the spec file so that packaging succeeds.

* Mon Aug 24 2009 Jonathan Perkin <jperkin@sun.com>

- Add conditionals for bundled zlib and innodb plugin

* Fri Aug 21 2009 Jonathan Perkin <jperkin@sun.com>

- Install plugin libraries in appropriate packages.
- Disable libdaemon_example and ftexample plugins.

* Thu Aug 20 2009 Jonathan Perkin <jperkin@sun.com>

- Update variable used for mysql-test suite location to match source.

* Fri Nov 07 2008 Joerg Bruehe <joerg@mysql.com>

- Correct yesterday's fix, so that it also works for the last flag,
  and fix a wrong quoting: un-quoted quote marks must not be escaped.

* Thu Nov 06 2008 Kent Boortz <kent.boortz@sun.com>

- Removed "mysql_upgrade_shell"
- Removed some copy/paste between debug and normal build

* Thu Nov 06 2008 Joerg Bruehe <joerg@mysql.com>

- Modify CFLAGS and CXXFLAGS such that a debug build is not optimized.
  This should cover both gcc and icc flags.  Fixes bug#40546.

* Fri Aug 29 2008 Kent Boortz <kent@mysql.com>

- Removed the "Federated" storage engine option, and enabled in all

* Tue Aug 26 2008 Joerg Bruehe <joerg@mysql.com>

- Get rid of the "warning: Installed (but unpackaged) file(s) found:"
  Some generated files aren't needed in RPMs:
  - the "sql-bench/" subdirectory
  Some files were missing:
  - /usr/share/aclocal/mysql.m4  ("devel" subpackage)
  - Manual "mysqlbug" ("server" subpackage)
  - Program "innochecksum" and its manual ("server" subpackage)
  - Manual "mysql_find_rows" ("client" subpackage)
  - Script "mysql_upgrade_shell" ("client" subpackage)
  - Program "ndb_cpcd" and its manual ("ndb-extra" subpackage)
  - Manuals "ndb_mgm" + "ndb_restore" ("ndb-tools" subpackage)

* Mon Mar 31 2008 Kent Boortz <kent@mysql.com>

- Made the "Federated" storage engine an option
- Made the "Cluster" storage engine and sub packages an option

* Wed Mar 19 2008 Joerg Bruehe <joerg@mysql.com>

- Add the man pages for "ndbd" and "ndb_mgmd".

* Mon Feb 18 2008 Timothy Smith <tim@mysql.com>

- Require a manual upgrade if the alread-installed mysql-server is
  from another vendor, or is of a different major version.

* Wed May 02 2007 Joerg Bruehe <joerg@mysql.com>

- "ndb_size.tmpl" is not needed any more,
  "man1/mysql_install_db.1" lacked the trailing '*'.

* Sat Apr 07 2007 Kent Boortz <kent@mysql.com>

- Removed man page for "mysql_create_system_tables"

* Wed Mar 21 2007 Daniel Fischer <df@mysql.com>

- Add debug server.

* Mon Mar 19 2007 Daniel Fischer <df@mysql.com>

- Remove Max RPMs; the server RPMs contain a mysqld compiled with all
  features that previously only were built into Max.

* Fri Mar 02 2007 Joerg Bruehe <joerg@mysql.com>

- Add several man pages for NDB which are now created.

* Fri Jan 05 2007 Kent Boortz <kent@mysql.com>

- Put back "libmygcc.a", found no real reason it was removed.

- Add CFLAGS to gcc call with --print-libgcc-file, to make sure the
  correct "libgcc.a" path is returned for the 32/64 bit architecture.

* Mon Dec 18 2006 Joerg Bruehe <joerg@mysql.com>

- Fix the move of "mysqlmanager" to section 8: Directory name was wrong.

* Thu Dec 14 2006 Joerg Bruehe <joerg@mysql.com>

- Include the new man pages for "my_print_defaults" and "mysql_tzinfo_to_sql"
  in the server RPM.
- The "mysqlmanager" man page got moved from section 1 to 8.

* Thu Nov 30 2006 Joerg Bruehe <joerg@mysql.com>

- Call "make install" using "benchdir_root=%%{_datadir}",
  because that is affecting the regression test suite as well.

* Thu Nov 16 2006 Joerg Bruehe <joerg@mysql.com>

- Explicitly note that the "MySQL-shared" RPMs (as built by MySQL AB)
  replace "mysql-shared" (as distributed by SuSE) to allow easy upgrading
  (bug#22081).

* Mon Nov 13 2006 Joerg Bruehe <joerg@mysql.com>

- Add "--with-partition" t 2006 Joerg Bruehe <joerg@mysql.com>

- Use the Perl script to run the tests, because it will automatically check
  whether the server is configured with SSL.

* Tue Jun 27 2006 Joerg Bruehe <joerg@mysql.com>

- move "mysqldumpslow" from the client RPM to the server RPM (bug#20216)

- Revert all previous attempts to call "mysql_upgrade" during RPM upgrade,
  there are some more aspects which need to be solved before this is possible.
  For now, just ensure the binary "mysql_upgrade" is delivered and installysql.com>

- To run "mysql_upgrade", we need a running server;
  start it in isolation and skip password checks.

* Sat May 20 2006 Kent Boortz <kent@mysql.com>

- Always compile for PIC, position independent code.

* Wed May 10 2006 Kent Boortz <kent@mysql.com>

- Use character set "all" when compiling with Cluster, to make Cluster
  nodes independent on the character set directory, and the problem
  that two RPM sub packages both wants to install this directory.

* Mon May 01 2006 Kent Boortz <kent@mysql.com>

- Use "./libtool --mode=execute" instead of searching for the
  executable in current directory and ".libs".

* Fri Apr 28 2006 Kent Boortz <kent@mysql.com>

- Install and run "mysql_upgrade"

* Wed Apr 12 2006 Jim Winstead <jimw@mysql.com>

- Remove sql-bench, and MySQL-bench RPM (will be built as an independent
  project from the mysql-bench repository)

* Tue Apr 11 2006 Jim Winstead <jimw@mysql.com>

- Remove old mysqltestmanager and related programs
* Sat Apr 01 2006 Kent Boortz <kent@mysql.com>

- Set $LDFLAGS from $MYSQL_BUILD_LDFLAGS

* Tue Mar 07 2006 Kent Boortz <kent@mysql.com>

- Changed product name from "Community Edition" to "Community Server"

* Mon Mar 06 2006 Kent Boortz <kent@mysql.com>

- Fast mutexes is now disabled by default, but should be
  used in Linux builds.

* Mon Feb 20 2006 Kent Boortz <kent@mysql.com>

- Reintroduced a max build
- Limited testing of 'debug' and 'max' servers
- Berkeley DB only in 'max'

* Mon Feb 13 2006 Joerg Bruehe <joerg@mysql.com>

- Use "-i" on "make test-force";
  this is essential for later evaluation of this log file.

* Thu Feb 09 2006 Kent Boortz <kent@mysql.com>

- Pass '-static' to libtool, link static with our own libraries, dynamic
  with system libraries.  Link with the bundled zlib.

* Wed Feb 08 2006 Kristian Nielsen <knielsen@mysql.com>

- Modified RPM spec to match new 5.1 debug+max combined community packaging.

* Sun Dec 18 2005 Kent Boortz <kent@mysql.com>

- Added "client/mysqlslap"

* Mon Dec 12 2005 Rodrigo Novo <rodrigo@mysql.com>

- Added zlib to the list of (static) libraries installed
- Added check against libtool wierdness (WRT: sql/mysqld || sql/.libs/mysqld)
- Compile MySQL with bundled zlib
- Fixed %%packager name to "MySQL Production Engineering Team"

* Mon Dec 05 2005 Joerg Bruehe <joerg@mysql.com>

- Avoid using the "bundled" zlib on "shared" builds:
  As it is not installed (on the build system), this gives dependency
  problems with "libtool" causing the build to fail.
  (Change was done on Nov 11, but left uncommented.)

* Tue Nov 22 2005 Joerg Bruehe <joerg@mysql.com>

- Extend the file existence check for "init.d/mysql" on un-install
  to also guard the call to "insserv"/"chkconfig".

* Thu Oct 27 2005 Lenz Grimmer <lenz@grimmer.com>

- added more man pages

* Wed Oct 19 2005 Kent Boortz <kent@mysql.com>

- Made yaSSL support an option (off by default)

* Wed Oct 19 2005 Kent Boortz <kent@mysql.com>

- Enabled yaSSL support

* Sat Oct 15 2005 Kent Boortz <kent@mysql.com>

- Give mode arguments the same way in all places
lenz@mysql.com>

- fixed the removing of the RPM_BUILD_ROOT in the %%clean section (the
  $RBR variable did not get expanded, thus leaving old build roots behind)

* Thu Aug 04 2005 Lenz Grimmer <lenz@mysql.com>

- Fixed the creation of the mysql user group account in the postinstall
  section (BUG 12348)
- Fixed enabling the Archive storage engine in the Max binary

* Tue Aug 02 2005 Lenz Grimmer <lenz@mysql.com>

- Fixed the Requires: tag for the server RPM (BUG 12233)

* Fri Jul 15 2005 Lenz Grimmer <lenz@mysql.com>

- create a "mysql" user group and assign the mysql user account to that group
  in the server postinstall section. (BUG 10984)

* Tue Jun 14 2005 Lenz Grimmer <lenz@mysql.com>

- Do not build statically on i386 by default, only when adding either "--with
  static" or "--define '_with_static 1'" to the RPM build options. Static
  linking really only makes sense when linking against the specially patched
  glibc 2.2.5.

* Mon Jun 06 2005 Lenz Grimmer <lenz@mysql.com>

- added mysql_client_test to the "bench" subpackage (BUG 10676)
- added the libndbclient static and shared libraries (BUG 10676)

* Wed Jun 01 2005 Lenz Grimmer <lenz@mysql.com>

- use "mysqldatadir" variable instead of hard-coding the path multiple times
- use the "mysqld_user" variable on all occasions a user name is referenced
- removed (incomplete) Brazilian translations
- removed redundant release tags from the subpackage descriptions

* Wed May 25 2005 Joerg Bruehe <joerg@mysql.com>

- Added a "make clean" between separate calls to "BuildMySQL".

* Thu May 12 2005 Guilhem Bichot <guilhem@mysql.com>

- Removed the mysql_tableinfo script made obsolete by the information schema

* Wed Apr 20 2005 Lenz Grimmer <lenz@mysql.com>

- Enabled the "blackhole" storage engine for the Max RPM

* Wed Apr 13 2005 Lenz Grimmer <lenz@mysql.com>

- removed the MySQL manual files (html/ps/texi) - they have been removed
  from the MySQL sources and are now available separately.

* Mon Apr 4 2005 Petr Chardin <petr@mysql.com>

- old mysqlmanager, mysq* Mon Feb 7 2005 Tomas Ulin <tomas@mysql.com>

- enabled the "Ndbcluster" storage engine for the max binary
- added extra make install in ndb subdir after Max build to get ndb binaries
- added packages for ndbcluster storage engine

* Fri Jan 14 2005 Lenz Grimmer <lenz@mysql.com>

- replaced obsoleted "BuildPrereq" with "BuildRequires" instead

* Thu Jan 13 2005 Lenz Grimmer <lenz@mysql.com>

- enabled the "Federated" storage engine for the max binary

* Tue Jan 04 2005 Petr Chardin <petr@mysql.com>

- ISAM and merge storage engines were purged. As well as appropriate
  tools and manpages (isamchk and isamlog)

* Fri Dec 31 2004 Lenz Grimmer <lenz@mysql.com>

- enabled the "Archive" storage engine for the max binary
- enabled the "CSV" storage engine for the max binary
- enabled the "Example" storage engine for the max binary

* Thu Aug 26 2004 Lenz Grimmer <lenz@mysql.com>

- MySQL-Max now requires MySQL-server instead of MySQL (BUG 3860)

* Fri Aug 20 2004 Lenz Grimmer <lenz@mysql.com>

- do not link statically on IA64/AMD64 as these systems do not have
  a patched glibc installed

* Tue Aug 10 2004 Lenz Grimmer <lenz@mysql.com>

- Added libmygcc.a to the devel subpackage (required to link applications
  against the the embedded server libmysqld.a) (BUG 4921)

* Mon Aug 09 2004 Lenz Grimmer <lenz@mysql.com>

- Added EXCEPTIONS-CLIENT to the "devel" package

* Thu Jul 29 2004 Lenz Grimmer <lenz@mysql.com>

- disabled OpenSSL in the Max binaries again (the RPM packages were the
  only exception to this anyway) (BUG 1043)

* Wed Jun 30 2004 Lenz Grimmer <lenz@mysql.com>

- fixed server postinstall (mysql_install_db was called with the wrong
  parameter)

* Thu Jun 24 2004 Lenz Grimmer <lenz@mysql.com>

- added mysql_tzinfo_to_sql to the server subpackage
- run "make clean" instead of "make distclean"

* Mon Apr 05 2004 Lenz Grimmer <lenz@mysql.com>

- added ncurses-devel to the build prerequisites (BUG 3377)

* Thu Feb 12 2004 Lenz Grimmer <lenz@mysql.com>

- when using gcc, _always_ use CXX=gcc
- replaced Copyright with License field (Copyright is obsolete)

* Tue Feb 03 2004 Lenz Grimmer <lenz@mysql.com>

- added myisam_ftdump to the Server package

* Tue Jan 13 2004 Lenz Grimmer <lenz@mysql.com>

- link the mysql client against libreadline instead of libedit (BUG 2289)

* Mon Dec 22 2003 Lenz Grimmer <lenz@mysql.com>

- marked /etc/logrotate.d/mysql as a config file (BUG 2156)

* Sat Dec 13 2003 Lenz Grimmer <lenz@mysql.com>

- fixed file permissions (BUG 1672)

* Thu Dec 11 2003 Lenz Grimmer <lenz@mysql.com>

- made testing for gcc3 a bit more robust

* Fri Dec 05 2003 Lenz Grimmer <lenz@mysql.com>

- added missing file mysql_create_system_tables to the server subpackage

* Fri Nov 21 2003 Lenz Grimmer <lenz@mysql.com>

- removed dependency on MySQL-client from the MySQL-devel subpackage
  as it is not really required. (BUG 1610)

* Fri Aug 29 2003 Lenz Grimmer <lenz@mysql.com>

- Fixed BUG 1162 (removed macro names from the changelog)
- Really fixed BUG 998 (disable the checking for installed but
  unpackaged files)

* Tue Aug 05 2003 Lenz Grimmer <lenz@mysql.com>

- Fixed BUG 959 (libmysqld not being compiled properly)
- Fixed BUG 998 (RPM build errors): added missing files to the
  distribution (mysql_fix_extensions, mysql_tableinfo, mysqldumpslow,
  mysql_fix_privilege_tables.1), removed "-n" from install section.

* Wed Jul 09 2003 Lenz Grimmer <lenz@mysql.com>

- removed the GIF Icon (file was not included in the sources anyway)
- removed unused variable shared_lib_version
- do not run automake before building the standard binary
  (should not be necessary)
- add server suffix '-standard' to standard binary (to be in line
  with the binary tarball distributions)
- Use more RPM macros (_exec_prefix, _sbindir, _libdir, _sysconfdir,
  _datadir, _includedir) throughout the spec file.
- allow overriding CC and CXX (required when building with other compilers)

* Fri May 16 2003 Lenz Grimmer <lenz@mysql.com>

- re-enabled RAID again

* Wed Apr 30 2003 Lenz Grimmer <lenz@mysql.com>

- disabled MyISAM RAID (--with-raid)- it throws an assertion which
  needs to be investigated first.

* Mon Mar 10 2003 Lenz Grimmer <lenz@mysql.com>

- added missing file mysql_secure_installation to server subpackage
  (BUG 141)

* Tue Feb 11 2003 Lenz Grimmer <lenz@mysql.com>

- re-added missing pre- and post(un)install scripts to server subpackage
- added config file /etc/my.cnf to the file list (just for completeness)
- make sure to create the datadir with 755 permissions

* Mon Jan 27 2003 Lenz Grimmer <lenz@mysql.com>

- removed unusedql.com>

- Reworked the build steps a little bit: the Max binary is supposed
  to include OpenSSL, which cannot be linked statically, thus trying
  to statically link against a special glibc is futile anyway
- because of this, it is not required to make yet another build run
  just to compile the shared libs (saves a lot of time)
- updated package description of the Max subpackage
- clean up the BuildRoot directory afterwards

* Mon Jul 15 2002 Lenz Grimmer <lenz@mysql.com>

- Updated Packager information
- Fixed the build options: the regular package is supposed to
  include InnoDB and linked statically, while the Max package
  should include BDB and SSL support

* Fri May 03 2002 Lenz Grimmer <lenz@mysql.com>

- Use more RPM macros (e.g. infodir, mandir) to make the spec
  file more portable
- reorganized the installation of documentation files: let RPM
  take care of this
- reorganized the file list: actually install man pages along
  with the binaries of the respective subpackage
- do not include libmysqld.a in the devel subpackage as well, if we
  have a special "embedded" subpackage
- reworked the package descriptions

* Mon Oct  8 2001 Monty

- Added embedded server as a separate RPM

* Fri Apr 13 2001 Monty

- Added mysqld-max to the distribution

* Tue Jan 2  2001  Monty

- Added mysql-test to the bench package

* Fri Aug 18 2000 Tim Smith <tim@mysql.com>

- Added separate libmysql_r directory; now both a threaded
  and non-threaded library is shipped.

* Tue Sep 28 1999 David Axmark <davida@mysql.com>

- Added the support-files/my-example.cnf to the docs directory.

- Removed devel dependency on base since it is about client
  development.

* Wed Sep 8 1999 David Axmark <davida@mysql.com>

- Cleaned up some for 3.23.

* Thu Jul 1 1999 David Axmark <davida@mysql.com>

- Added support for shared libraries in a separate sub
  package. Original fix by David Fox (dsfox@cogsci.ucsd.edu)

- The --enable-assembler switch is now automatically disables on
  platforms there assembler code is unavailable. This should allow
  building this RPM on non i386 systems.

* Mon Feb 22 1999 David Axmark <david@detron.se>

- Removed unportable cc switches from the spec file. The defaults can
  now be overridden with environment variables. This feature is used
  to compile the official RPM with optimal (but compiler version
  specific) switches.

- Removed the repetitive description parts for the sub rpms. Maybe add
  again if RPM gets a multiline macro capability.

- Added support for a pt_BR translation. Translation contributed by
  Jorge Godoy <jorge@bestway.com.br>.

* Wed Nov 4 1998 David Axmark <david@detron.se>

- A lot of changes in all the rpm and install scripts. This may even
  be a working RPM :-)

* Sun Aug 16 1998 David Axmark <david@detron.se>

- A developers changelog for MySQL is available in the source RPM. And
  there is a history of major user visible changed in the Reference
  Manual.  Only RPM specific changes will be documented here.
