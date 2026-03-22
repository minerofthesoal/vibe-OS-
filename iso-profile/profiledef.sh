#!/usr/bin/env bash
# shellcheck disable=SC2034
# vibeOS archiso profile definition

iso_name="vibeos"
iso_label="VIBEOS_$(date +%Y%m)"
iso_publisher="vibeOS <https://github.com/minerofthesoal/vibe-OS->"
iso_application="vibeOS Live/Installer"
iso_version="$(date +%Y.%m.%d)"
install_dir="arch"
buildmodes=('iso')
bootmodes=(
  'bios.syslinux.mbr'
  'bios.syslinux.eltorito'
  'uefi-ia32.grub.esp'
  'uefi-x64.grub.esp'
  'uefi-ia32.grub.eltorito'
  'uefi-x64.grub.eltorito'
)
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'xz' '-Xbcj' 'x86' '-b' '1M' '-Xdict-size' '1M')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/etc/gshadow"]="0:0:400"
  ["/etc/profile.d/vibeos-live.sh"]="0:0:755"
  ["/usr/local/bin/vibeos-installer"]="0:0:755"
  ["/usr/local/bin/vibeos-firstboot"]="0:0:755"
  ["/usr/local/bin/vibeos-setup-live"]="0:0:755"
  ["/opt/vibeos/scripts/utils.sh"]="0:0:755"
  ["/opt/vibeos/scripts/01-hardware-detect.sh"]="0:0:755"
  ["/opt/vibeos/scripts/02-partition-disk.sh"]="0:0:755"
  ["/opt/vibeos/scripts/03-base-install.sh"]="0:0:755"
  ["/opt/vibeos/scripts/04-chroot-configure.sh"]="0:0:755"
  ["/opt/vibeos/scripts/05-install-de.sh"]="0:0:755"
  ["/opt/vibeos/scripts/06-finalize.sh"]="0:0:755"
)
