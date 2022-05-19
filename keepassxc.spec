%undefine __cmake_in_source_build
# EPEL7 not possible because libgcrypt version is 1.5

Name:           keepassxc
Version:        2.7.1
Release:        3%{?dist}
Summary:        Cross-platform password manager
License:        Boost and BSD and CC0 and GPLv3 and LGPLv2 and LGPLv2+ and LGPLv3+ and Public Domain
URL:            http://www.keepassxc.org/
Source0:        https://github.com/keepassxreboot/keepassxc/releases/download/%{version}/keepassxc-%{version}-src.tar.xz
# Patch0: fixes GNOME quirks on Wayland sessions. Read
# https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/message/3BVLBS4B3XHJEXFVGD7RK2ZMXZG6JQZT/
# read also https://github.com/keepassxreboot/keepassxc/pull/3520/files
#
# Patch0 improved by pewpeww https://src.fedoraproject.org/rpms/keepassxc/pull-request/1
#
# 23 March 2022 Germano Massullo's update: Jan Grulich said that Qt patch https://code.qt.io/cgit/qt/qtbase.git/commit/?id=dda7dab8274991e4a61a97c352d4367f8f815bb9
# is included in qt5-qtbase in all Fedora versions since 32, even before it landed upstream, but it is not in RHEL qt5-qtbase package.
# So I think it is no longer needed in Fedora
# 
# Concerning upstream Qt6 version, the patch was reverted and kept for Qt 6.3, but concerning keepassxc it is not important since it uses Qt 5
#
# 29 April 2022 Germano Massullo's update: users in upstream bugreports
# https://github.com/keepassxreboot/keepassxc/issues/7959
# https://github.com/keepassxreboot/keepassxc/issues/5608
# are reporting regression. I am resuming xcb.patch to all branches
#

Patch0:         xcb.patch


BuildRequires:  botan2-devel
BuildRequires:  cmake >= 3.1
BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++ >= 4.7
BuildRequires:  libappstream-glib
BuildRequires:  libargon2-devel
BuildRequires:  libcurl-devel
BuildRequires:  libgcrypt-devel >= 1.7
BuildRequires:  libmicrohttpd-devel
BuildRequires:  libsodium-devel
BuildRequires:  libusb1-devel
BuildRequires:  libXi-devel
BuildRequires:  libXtst-devel
BuildRequires:  libyubikey-devel
BuildRequires:  minizip-devel
BuildRequires:  pcsc-lite-devel
BuildRequires:  qrencode-devel
BuildRequires:  readline-devel
BuildRequires:  qt5-qtbase-devel >= 5.2
BuildRequires:  qt5-qtbase-private-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qttools-devel >= 5.2
BuildRequires:  qt5-qtx11extras-devel
BuildRequires:  ykpers-devel
BuildRequires:  zlib-devel

# For EL8 missing rubygem-asciidoctor read
# https://bugzilla.redhat.com/show_bug.cgi?id=1859390
# https://bugzilla.redhat.com/show_bug.cgi?id=1820896
%if 0%{?fedora}
BuildRequires:  rubygem-asciidoctor
%endif

# enforces on the user system, Qt version to be the same one used to build KeepassXC
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}

# KeePassXC bundles the ykcore code due to lack of support from Yubico and
# stratification of version across various operating system distros. Additionally,
# KeePassXC has modified the API of ykcore to make it more functional when using
# non-YubiKey keys (ie, OnlyKey).
Provides: bundled(ykcore)

%description
KeePassXC is a community fork of KeePassX
KeePassXC is an application for people with extremely high demands on secure
personal data management.
KeePassXC saves many different information e.g. user names, passwords, urls,
attachemts and comments in one single database. For a better management
user-defined titles and icons can be specified for each single entry.
Furthermore the entries are sorted in groups, which are customizable as well.
The integrated search function allows to search in a single group or the
complete database.
KeePassXC offers a little utility for secure password generation. The password
generator is very customizable, fast and easy to use. Especially someone who
generates passwords frequently will appreciate this feature.
The complete database is always encrypted either with AES (alias Rijndael) or
Twofish encryption algorithm using a 256 bit key. Therefore the saved
information can be considered as quite safe.



%prep
%autosetup -p1

%build
# This package fails to build with LTO due to undefined symbols.  LTO
# was disabled in OpenSuSE as well, but with no real explanation why
# beyond the undefined symbols.  It really shold be investigated further.
# Disable LTO
%define _lto_cflags %{nil}
%if 0%{?fedora}
%cmake \
    -DWITH_TESTS=OFF \
    -DWITH_XC_ALL=ON \
    -DWITH_XC_KEESHARE_SECURE=ON \
    -DWITH_XC_UPDATECHECK=OFF \
    -DCMAKE_BUILD_TYPE=Release
%endif
# -DWITH_XC_DOCS=OFF is needed on EL due missing rubygem-asciidoctor
# For EL8 missing rubygem-asciidoctor read
# https://bugzilla.redhat.com/show_bug.cgi?id=1859390
# https://bugzilla.redhat.com/show_bug.cgi?id=1820896
%if 0%{?el8}
%cmake \
    -DWITH_TESTS=OFF \
    -DWITH_XC_ALL=ON \
    -DWITH_XC_KEESHARE_SECURE=ON \
    -DWITH_XC_UPDATECHECK=OFF \
    -DWITH_XC_DOCS=OFF \
    -DCMAKE_BUILD_TYPE=Release
%endif
%if 0%{?el9}
%cmake \
    -DWITH_TESTS=OFF \
    -DWITH_XC_ALL=ON \
    -DWITH_XC_KEESHARE_SECURE=ON \
    -DWITH_XC_UPDATECHECK=OFF \
    -DWITH_XC_DOCS=OFF \
    -DCMAKE_BUILD_TYPE=Release
%endif
%cmake_build
 
%install
%cmake_install
 
desktop-file-install \
    --dir %{buildroot}%{_datadir}/applications \
    --delete-original \
    --add-mime-type application/x-keepassxc \
    %{buildroot}%{_datadir}/applications/org.%{name}.KeePassXC.desktop
 
# Associate KDB* files
cat > x-keepassxc.desktop << EOF
[Desktop Entry]
Comment=
Hidden=false
Icon=keepassxc.png
MimeType=application/x-keepassxc
Patterns=*.kdb;*.KDB;*.kdbx;*.KDBX*
Type=MimeType
EOF
install -D -m 644 -p x-keepassxc.desktop \
    %{buildroot}%{_datadir}/mimelnk/application/x-keepassxc.desktop

#install appdata files

%find_lang %{name} --with-qt

%check
%ctest
desktop-file-validate %{buildroot}%{_datadir}/applications/org.%{name}.KeePassXC.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/org.%{name}.KeePassXC.appdata.xml

%files -f %{name}.lang
%doc README.md
%license COPYING LICENSE*
%{_bindir}/keepassxc
%{_bindir}/keepassxc-cli
%{_bindir}/keepassxc-proxy
%{_datadir}/keepassxc
%{_datadir}/keepassxc/wordlists
%{_datadir}/applications/org.%{name}.KeePassXC.desktop
%{_datadir}/metainfo/org.%{name}.KeePassXC.appdata.xml
%{_datadir}/mimelnk
%{_datadir}/mime/packages/*.xml
%{_datadir}/icons/hicolor/*/*/*keepassxc*
%{_libdir}/%{name}
# Missing rubygem-asciidoctor in EL8 does not allow having documentation in EL8
# Read https://bugzilla.redhat.com/show_bug.cgi?id=1859390
%if 0%{?fedora}
%{_mandir}/man1/%{name}-cli.1*
%{_mandir}/man1/%{name}.1*
%endif

%changelog
* Fri Apr 29 2022 Germano Massullo <germano.massullo@gmail.com> - 2.7.1-3
- enabled Patch0:xcb.patch for all branches

* Mon Apr 11 2022 Germano Massullo <germano.massullo@gmail.com> - 2.7.1-2
- replaces BuildRequires: minizip-compat-devel with BuildRequires: minizip-devel

* Wed Apr 06 2022 Germano Massullo <germano.massullo@gmail.com> - 2.7.1-1
- 2.7.1 release

* Tue Mar 22 2022 Germano Massullo <germano.massullo@gmail.com> - 2.7.0-1
- 2.7.0 release
- adds BuildRequires: botan2-devel
- adds BuildRequires: pcsc-lite-devel
- adds Provides: bundled(ykcore)
- enforcing on the user system, Qt version to be the same one used to build KeepassXC
- replaces BuildRequires: quazip-qt5-devel with BuildRequires: minizip-compat-devel

* Tue Mar 08 2022 Jan Grulich <jgrulich@redhat.com> - 2.6.6-6
- Rebuild (qt5)

* Mon Feb 21 2022 Germano Massullo <germano.massullo@gmail.com> - 2.6.6-5
- User pewpeww improved xcb.patch - https://src.fedoraproject.org/rpms/keepassxc/pull-request/1

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Thu Aug 19 2021 Björn Esser <besser82@fedoraproject.org> - 2.6.6-3
- Rebuild (quazip)

* Thu Jul 22 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Mon Jun 14 2021 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.6.6-1
- Update to 2.6.6

* Sat May 01 2021 Germano Massullo <germano.massullo@gmail.com> - 2.6.4-2
- added xcb.patch that fixes GNOME quirks on Wayland sessions. Read https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/message/3BVLBS4B3XHJEXFVGD7RK2ZMXZG6JQZT/

* Sun Jan 31 2021 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.6.4-1
- Update to 2.6.4

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Jan 21 2021 Germano Massullo <germano.massullo@gmail.com> - 2.6.3-2
- EL8: disabled documentation, removed rubygem-asciidoctor and quazip depencendies. For bugzilla tickets about missing dependencies, read this spec file near Fedora/EL8 macros

* Wed Jan 13 2021 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.6.3-1
- Update to 2.6.3

* Mon Oct 26 2020 Germano Massullo <germano.massullo@gmail.com> - 2.6.2-2
- replaced -WITH_XC_UPDATECHECK=OFF with -DWITH_XC_UPDATECHECK=OFF Read https://bugzilla.redhat.com/show_bug.cgi?id=1887609

* Fri Oct 23 2020 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.6.2-1
- Update to 2.6.2

* Thu Aug 20 2020 Germano Massullo <germano.massullo@gmail.com> - 2.6.1-1
- 2.6.1 release

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 07 2020 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.6.0-1
- Update to 2.6.0

* Wed Jul 01 2020 Jeff Law <law@redhat.com> - 2.5.4-2
- Diable LTO

* Thu Apr 09 2020 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.5.4-1
- Update to 2.5.4

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.5.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Jan 20 2020 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.5.3-1
- Update to 2.5.3

* Sun Jan 05 2020 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.5.2-1
- Update to 2.5.2

* Tue Nov 12 2019 Germano Massullo <germano.massullo@gmail.com> - 2.5.1-1
- 2.5.1 release

* Mon Oct 28 2019 Gwyn Ciesla <gwync@protonmail.com> - 2.5.0-1
- 2.5.0

* Thu Sep 19 2019 Germano Massullo <germano.massullo@gmail.com> - 2.4.3-6
- Replaced BuildRequires: quazip-devel with BuildRequires: quazip-qt5-devel

* Mon Sep 16 2019 Germano Massullo <germano.massullo@gmail.com> - 2.4.3-5
- Added BuildRequires: quazip-devel

* Thu Sep 05 2019 Germano Massullo <germano.massullo@gmail.com> - 2.4.3-4
- Added -DWITH_XC_KEESHARE_SECURE=ON

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Jun 25 2019 Björn Esser <besser82@fedoraproject.org> - 2.4.3-2
- Rebuilt (libqrencode.so.4)

* Tue Jun 11 2019 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.4.3-1
- Update to 2.4.3

* Fri May 31 2019 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.4.2-1
- Update to 2.4.2

* Tue Apr 16 2019 Germano Massullo <germano.massullo@gmail.com> - 2.4.1-1
- 2.4.1 release
- Added WITH_XC_UPDATECHECK=OFF

* Wed Mar 20 2019 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.4.0-1
- Update to 2.4.0
- Drop unneeded sed lines in spec file
- Added BR for qrencode-devel and qt5-qtsvg-devel

* Mon Mar 18 2019 Remi Collet <remi@fedoraproject.org> - 2.3.4-3
- rebuild for libargon2 new soname

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Aug 29 2018 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.3.4-1
- Update to 2.3.4

* Thu Jul 19 2018 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.3.3-3
- Fix FTBFS

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu May 10 2018 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.3.3-1
- Update to 2.3.3

* Tue May 08 2018 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.3.2-1
- Update to 2.3.2

* Wed Mar 07 2018 Germano Massullo <germano.massullo@gmail.com> - 2.3.1-1
- 2.3.1 release
- used -DWITH_XC_ALL=ON to enable all features. Read https://github.com/keepassxreboot/keepassxc/issues/1558#issuecomment-369291706

* Wed Feb 28 2018 Germano Massullo <germano.massullo@gmail.com> - 2.2.4-7
- added BuildRequires: libargon2-devel
- added BuildRequires: libcurl-devel
- added BuildRequires: libgcrypt-devel >= 1.7
- added BuildRequires: libsodium-devel
- added BuildRequires: gcc-c++ >= 4.7
- added %%{_mandir}/man1/%{name}-cli.1*

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 2.2.4-6
- Escape macros in %%changelog

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Jan 05 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 2.2.4-4
- Remove obsolete scriptlets

* Wed Dec 27 2017 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.2.4-3
- Fix specfile error

* Sat Dec 16 2017 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.2.4-2
- Adjust for changes in appdata and desktop filename change

* Thu Dec 14 2017 Germano Massullo <germano.massullo@gmail.com> - 2.2.4-1
- 2.2.4 release
- removed patch to fix typo in a XML tag

* Tue Dec 12 2017 Germano Massullo <germano.massullo@gmail.com> - 2.2.3-1
- 2.2.3 release
- added patch to fix typo in a XML tag

* Sun Oct 22 2017 Mukundan Ragavan <nonamedotc@fedoraproject.org> - 2.2.2-1
- Update to 2.2.2
- Fix desktop file names
- Added BR on libappstream-glib
- Install appdata file

* Mon Oct 02 2017 Germano Massullo <germano.massullo@gmail.com> - 2.2.1-1
- 2.2.1 release

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jun 26 2017 Germano Massullo <germano.massullo@gmail.com> - 2.2.0-1
- 2.2.0 release
- added %%{_bindir}/keepassxc-cli
- changed -DWITH_XC_YUBIKEY=OFF to -DWITH_XC_YUBIKEY=ON
- added BuildRequires: ykpers-devel and BuildRequires: libyubikey-devel

* Fri May 19 2017 Germano Massullo <germano.massullo@gmail.com> - 2.1.4-2
- Disabled Yubikey support. It will be re-enabled on 2.2.0 release

* Sun May 14 2017 Germano Massullo <germano.massullo@gmail.com> - 2.1.4-1
- First release on Fedora repository
