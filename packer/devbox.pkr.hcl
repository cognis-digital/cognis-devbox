# Build a KVM/QEMU qcow2 dev image with everything preinstalled.
#   packer init . && packer build .
packer { required_plugins { qemu = { source = "github.com/hashicorp/qemu", version = "~> 1" } } }
source "qemu" "devbox" {
  iso_url          = "https://releases.ubuntu.com/22.04/ubuntu-22.04.4-live-server-amd64.iso"
  iso_checksum     = "auto"
  output_directory = "output-devbox"
  disk_size        = "40000"
  format           = "qcow2"
  accelerator      = "kvm"
  ssh_username     = "cognis"
  ssh_password     = "cognis"
  ssh_timeout      = "30m"
  vm_name          = "cognis-devbox.qcow2"
  cpus             = 4
  memory           = 8192
}
build {
  sources = ["source.qemu.devbox"]
  provisioner "shell" { script = "provision/install-all.sh" }
}
