# TODO:
# - mplayer.sh:
#   - patch to allow playing audio files (currently insists to find video)
#   - audio CD support?

Name:           vdr-mp3
Version:        0.10.4
Release:        3%{?dist}
Summary:        Sound playback plugin for VDR
License:        GPLv2+
URL:            https://github.com/vdr-projects/vdr-plugin-mp3/
Source0:        https://github.com/vdr-projects/vdr-plugin-mp3/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        http://batleth.sapienti-sat.org/projects/VDR/versions/mplayer.sh-0.8.7.tar.gz 
Source2:        %{name}-mediasources.sh
Source3:        %{name}-mp3.conf
Source4:        %{name}-mplayer.conf
Source5:        %{name}-mplayer-minimal.sh
Source6:        %{name}-mp3sources.conf
Patch0:         %{name}-%{version}-Makefile.patch
Patch1:         %{name}-fix-overloaded-ambiguous.patch

BuildRequires:  gcc-c++
BuildRequires:  vdr-devel >= 2.0.6
BuildRequires:  libsndfile-devel >= 1.0.0
BuildRequires:  libvorbis-devel
BuildRequires:  %{__perl}
BuildRequires:  libmad-devel
BuildRequires:  libid3tag-devel
Requires:       vdr(abi)%{?_isa} = %{vdr_apiversion}
Requires:       netpbm-progs
Requires:       mjpegtools >= 1.8.0
Requires:       file

%description
The MP3 plugin adds audio playback capability to VDR.  Supported audio
formats are those supported by libmad, libsndfile and libvorbis.

%package     -n vdr-mplayer
Summary:        MPlayer plugin for VDR
Group:          Applications/Multimedia
BuildRequires:  %{__perl}
Requires:       vdr(abi)%{?_isa} = %{vdr_apiversion}
Requires:       mplayer >= 1.0

%description -n vdr-mplayer
The MPlayer plugin adds the ability to call MPlayer from within VDR,
allowing to replay all video formats supported by MPlayer over VDR's
primary output device.


%prep
%setup -q -n vdr-plugin-mp3-%{version} -a 1
%patch0 -p1
%patch1 -p1
%{__perl} -pi -e \
  's|CFGFIL=.*|CFGFIL="%{vdr_configdir}/plugins/mplayer.sh.conf"|' \
  mplayer.sh
%{__perl} -pi -e \
  's|"/var/cache/images/mp3"|"%{vdr_cachedir}/mp3/images"|' \
  data-mp3.c README
%{__perl} -pi -e \
  's|"/video/plugins/DVD-VCD"|"%{vdr_resdir}/DVD-VCD"| ;
   s|^MPLAYER=.*|MPLAYER="%{_bindir}/mplayer"|' \
  mplayer.sh.conf
for f in HISTORY MANUAL README ; do
  iconv -f iso-8859-1 -t utf-8 $f > $f.utf-8 ; mv $f.utf-8 $f
done
sed -e 's|/var/lib/vdr|%{vdr_vardir}|' %{SOURCE4} > %{name}-mplayer.conf


%build
%make_build LIBDIR=. VDRDIR=%{_libdir}/vdr WITH_OSS_OUTPUT=1 \
    libvdr-mp3.so libvdr-mplayer.so
echo "%{vdr_resdir}/DVD-VCD;DVD or VCD;0" > mplayersources.conf


%install
# Common dirs
install -dm 755 $RPM_BUILD_ROOT%{vdr_plugindir}
install -dm 755 $RPM_BUILD_ROOT%{vdr_configdir}/plugins
install -dm 755 $RPM_BUILD_ROOT%{vdr_plugindir}/bin
install -dm 755 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/vdr-plugins.d

# Common files
install -pm 755 %{SOURCE2} $RPM_BUILD_ROOT%{vdr_plugindir}/bin/mediasources.sh
install -pm 755 examples/mount.sh.example \
  $RPM_BUILD_ROOT%{vdr_plugindir}/bin/mount.sh

# MP3 files
install -pm 755 libvdr-mp3.so.%{vdr_apiversion} $RPM_BUILD_ROOT%{vdr_plugindir}
install -pm 644 %{SOURCE6} $RPM_BUILD_ROOT%{vdr_configdir}/plugins/mp3sources.conf
install -pm 755 examples/image_convert.sh.example \
  $RPM_BUILD_ROOT%{vdr_plugindir}/bin/image_convert.sh
%{__perl} -pe 's|/var/cache/vdr/|%{vdr_cachedir}/|' %{SOURCE3} \
  > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/vdr-plugins.d/mp3.conf
chmod 644 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/vdr-plugins.d/mp3.conf
install -dm 755 $RPM_BUILD_ROOT%{vdr_cachedir}/mp3/images
i=$RPM_BUILD_ROOT%{vdr_cachedir}/mp3/id3info.cache ; > $i ; chmod 644 $i

# MPlayer files
install -pm 755 libvdr-mplayer.so.%{vdr_apiversion} $RPM_BUILD_ROOT%{vdr_plugindir}
install -dm 755 $RPM_BUILD_ROOT%{vdr_resdir}/DVD-VCD
touch $RPM_BUILD_ROOT%{vdr_resdir}/DVD-VCD/{DVD,VCD}
chmod 644 $RPM_BUILD_ROOT%{vdr_resdir}/DVD-VCD/*
install -pm 644 mplayersources.conf mplayer.sh.conf \
  $RPM_BUILD_ROOT%{vdr_configdir}/plugins
install -pm 755 mplayer.sh $RPM_BUILD_ROOT%{vdr_plugindir}/bin/mplayer.sh
install -pm 755 %{SOURCE5} $RPM_BUILD_ROOT%{vdr_plugindir}/bin/mplayer-minimal.sh
install -pm 644 %{name}-mplayer.conf \
  $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/vdr-plugins.d/mplayer.conf
install -dm 755 $RPM_BUILD_ROOT%{vdr_vardir}
i=$RPM_BUILD_ROOT%{vdr_vardir}/global.mplayer.resume ; > $i ; chmod 644 $i


%post
if [ $1 -eq 1 ] ; then
  %{vdr_plugindir}/bin/mediasources.sh \
    >> %{vdr_configdir}/plugins/mp3sources.conf || :
else
  r=global.mplayer.resume
  if [ -f %{vdr_videodir}/$r -a ! -f %{vdr_vardir}/$r ] ; then
    mv %{vdr_videodir}/$r %{vdr_vardir}/$r
  fi
fi

%post -n vdr-mplayer
if [ $1 -eq 1 ] ; then
  %{vdr_plugindir}/bin/mediasources.sh \
    >> %{vdr_configdir}/plugins/mplayersources.conf || :
fi


%files
%defattr(-,root,root,-)
%doc HISTORY MANUAL README examples/mount.sh.example
%doc examples/mp3sources.conf.example examples/network.sh.example
%license COPYING
%config(noreplace) %{vdr_configdir}/plugins/mp3sources.conf
%config(noreplace) %{_sysconfdir}/sysconfig/vdr-plugins.d/mp3.conf
%{vdr_plugindir}/libvdr-mp3.so.%{vdr_apiversion}
%{vdr_plugindir}/bin/image_convert.sh
%{vdr_plugindir}/bin/mediasources.sh
%{vdr_plugindir}/bin/mount.sh
%defattr(-,%{vdr_user},root,-)
%dir %{vdr_cachedir}/mp3/
%dir %{vdr_cachedir}/mp3/images/
%ghost %{vdr_cachedir}/mp3/id3info.cache

%files -n vdr-mplayer
%defattr(-,root,root,-)
%doc HISTORY MANUAL README examples/mplayer.sh.example
%doc examples/mount.sh.example
%license COPYING
%config(noreplace) %{vdr_configdir}/plugins/mplayer*.conf
%config(noreplace) %{_sysconfdir}/sysconfig/vdr-plugins.d/mplayer.conf
%{vdr_plugindir}/libvdr-mplayer.so.%{vdr_apiversion}
%{vdr_plugindir}/bin/mediasources.sh
%{vdr_plugindir}/bin/mount.sh
%{vdr_plugindir}/bin/mplayer*.sh
%{vdr_resdir}/DVD-VCD/
%defattr(-,%{vdr_user},root,-)
%ghost %{vdr_vardir}/global.mplayer.resume

%changelog
* Thu Dec 30 2021 Martin Gansser <martinkg@fedoraproject.org> -  0.10.4-3
- Rebuilt for new VDR API version

* Tue Aug 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.10.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Wed May 26 2021 Martin Gansser <martinkg@fedoraproject.org> - 0.10.4-1
- Use fork because its under maintenance

* Fri Apr 30 2021 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-30
- Rebuilt for new VDR API version

* Thu Feb 04 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.10.2-29
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jan 04 2021 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-28
- Rebuilt for new VDR API version
- Add vdr-mp3-fix-C++11-warning.patch that fixes:

* Wed Oct 21 2020 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-27
- Rebuilt for new VDR API version

* Fri Aug 28 2020 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-26
- Rebuilt for new VDR API version

* Tue Aug 18 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.10.2-25
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Feb 05 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.10.2-24
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Aug 09 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.10.2-23
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Jul 01 2019 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-22
- Rebuilt for new VDR API version 2.4.1

* Sun Jun 30 2019 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-21
- Rebuilt for new VDR API version

* Tue Jun 18 2019 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-20
- Rebuilt for new VDR API version

* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.10.2-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Oct 11 2018 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-18
- Add BR gcc-c++

* Sun Aug 19 2018 Leigh Scott <leigh123linux@googlemail.com> - 0.10.2-17
- Rebuilt for Fedora 29 Mass Rebuild binutils issue

* Fri Jul 27 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.10.2-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Apr 18 2018 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-15
- Rebuilt for vdr-2.4.0

* Thu Mar 01 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 0.10.2-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 0.10.2-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Mar 21 2017 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-12
- Add vdr-mp3-fix-overloaded-ambiguous.patch

* Tue Mar 17 2015 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-11
- added vdr-mp3-vdr2.1.2-compat.patch
- mark license files as %%license where available

* Mon Sep 01 2014 Sérgio Basto <sergio@serjux.com> - 0.10.2-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Mar 30 2014 Martin Gansser <martinkg@fedoraproject.org> - 0.10.2-9
- Rebuild

* Mon May 27 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.10.2-8
- Rebuilt for x264/FFmpeg

* Sun Apr 28 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.10.2-7
- https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Oct 3 2012 Martin Gansser <linux4martin@gmx.de> - 0.10.2-6
- spec file cleanup
- spell checking in %%changelog section

* Wed Oct 3 2012 Martin Gansser <linux4martin@gmx.de> - 0.10.2-5
- Adapt to VDR 1.7.30.
- changed vdr-devel BuildRequires for Fedora 18
- spec file cleanup
- rebuild for Fedora 18

* Sat May 19 2012 Martin Gansser <linux4martin@gmx.de> - 0.10.2-4
- reset the release tag to 1 for release update

* Tue May 15 2012 Martin Gansser <linux4martin@gmx.de> - 0.10.2-3
- added correct permissions for vdr_vardir and vdr_cachedir

* Mon May 14 2012 Martin Gansser <linux4martin@gmx.de> - 0.10.2-2
- more cleanups
- fixed the use of vdr macros

* Sun May 13 2012 Martin Gansser <linux4martin@gmx.de> - 0.10.2-1
- Rebuilt for new release

* Fri Mar 02 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.10.1-10
- Rebuilt for c++ ABI breakage

* Wed Feb 08 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.10.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.10.1-8
- rebuild for new F11 features

* Fri Nov 28 2008 Felix Kaechele <felix at fetzig dot org> - 0.10.1-7
- fixed another tiny error :)

* Fri Nov 28 2008 Felix Kaechele <felix at fetzig dot org> - 0.10.1-6
- fixed small error

* Fri Nov 28 2008 Felix Kaechele <felix at fetzig dot org> - 0.10.1-5
- removed all references to audiodir since it's not used by vdr core

* Mon Aug 04 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.10.1-4
- rebuild

* Tue Apr  8 2008 Ville Skyttä <ville.skytta at iki.fi> - 0.10.1-3
- Rebuild for VDR 1.6.0.

* Sun Mar 16 2008 Ville Skyttä <ville.skytta at iki.fi> - 0.10.1-2
- Suppress console debug messages.
- Add dxr3:prebuf example to mplayer.sh.conf.

* Mon Aug 27 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.10.1-1
- 0.10.1.

* Wed Aug 22 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.10.0-2
- License: GPLv2+

* Sun Jun 17 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.10.0-1
- 0.10.0.
- Fix path to mplayer in mplayer.sh.conf (full path needed after all).

* Sun Feb 25 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-5
- Apply upstream patch to check availability of last dir before accessing it.
- Update mplayer.sh to 0.8.7.

* Sun Jan  7 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-4
- Rebuild for VDR 1.4.5.

* Sat Nov  4 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-3
- Rebuild for VDR 1.4.4.

* Fri Oct 06 2006 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> 0.9.15-2
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Sat Sep 23 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-1
- 0.9.15, build for VDR 1.4.3.

* Sun Aug  6 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-0.6.pre14
- Rebuild for VDR 1.4.1-3.

* Sun Jul 30 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-0.5.pre14
- 0.9.15pre14 + Rolf Ahrenberg's Finnish patch.
- Plugin C(XX)FLAGS and zlib patches applied upstream.
- Re-enable MP3 plugin; it supposedly works just fine in most setups
  (still not in my vdr-dxr3 one though).

* Mon Jul 24 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-0.5.pre10
- Patch to get plugin C(XX)FLAGS properly applied from Make.config.

* Sun Jul 23 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-0.4.pre10
- Include accidentally dropped mplayer.sh.conf.

* Sun Jun 11 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-0.3.pre10
- Rebuild for VDR 1.4.1.

* Sun Apr 30 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-0.2.pre10
- 0.9.15pre10, build for VDR 1.4.0.
- Move -mplayer global resume file to /var/lib/vdr.

* Sun Apr 23 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-0.2.pre6
- Require versioned vdr(abi) also in -mplayer.

* Mon Apr 17 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.15-0.1.pre6
- 0.9.15pre6, i18n fix applied upstream.
- Rebuild/adjust for VDR 1.3.47, require versioned vdr(abi).
- Trim pre-RLO %%changelog entries.

* Sun Mar 26 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.14-8
- Rebuild for VDR 1.3.45.
- Disable mp3 plugin, it doesn't work properly with NPTL (#844).

* Sat Mar 18 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.14-7
- Get rid of superfluous direct dependency on zlib (#813).

* Sat Mar 18 2006 Thorsten Leemhuis <fedora at leemhuis.info> - 0.9.14-6
- drop 0.lvn from release

* Wed Mar  1 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.14-0.lvn.6
- Rebuild for VDR 1.3.44.

* Tue Feb 28 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- add dist

* Sun Feb 19 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.14-0.lvn.5
- Rebuild for VDR 1.3.43.

* Sun Feb  5 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.14-0.lvn.4
- Rebuild for VDR 1.3.42.

* Sun Jan 22 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.14-0.lvn.3
- Fix button translations with VDR >= 1.3.38.
- Add mplayer-minimal.sh, an alternative MPlayer launcher script.
- Rebuild for VDR 1.3.40.

* Sun Jan 15 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.14-0.lvn.2
- Rebuild for VDR 1.3.39.

* Sun Jan  8 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.9.14-0.lvn.1
- 0.9.14.
- Patch to fix build with gcc 4.1.
- Rebuild for VDR 1.3.38.

* Mon Nov 28 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.13-1.lvn.10
- Rebuild for VDR 1.3.37.

* Sun Nov  6 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.13-1.lvn.9
- Rebuild for VDR 1.3.36.

* Tue Nov  1 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.13-1.lvn.8
- Rebuild for VDR 1.3.35.

* Mon Oct  3 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.13-1.lvn.7
- Rebuild for VDR 1.3.34.

* Sun Sep 25 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.13-1.lvn.6
- Rebuild for VDR 1.3.33.

* Sun Sep 11 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.13-1.lvn.5
- Rebuild for VDR 1.3.32.

* Sun Aug 28 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.13-1.lvn.4
- Rebuild for VDR 1.3.31.

* Sun Aug 21 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.13-1.lvn.3
- Rebuild for VDR 1.3.30.
- Add audiodir to mp3sources.conf.

* Tue Aug 16 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.13-1.lvn.2
- Try to avoid build system problems by not using %%expand with vdr-config.

* Sat Aug 13 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.13-1.lvn.1
- Improve descriptions, convert docs to UTF-8.
