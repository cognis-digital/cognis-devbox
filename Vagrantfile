Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.hostname = "cognis-devbox"
  config.vm.provider "libvirt" do |v| v.memory = 8192; v.cpus = 4 end
  config.vm.provider "virtualbox" do |v| v.memory = 8192; v.cpus = 4 end
  config.vm.provision "shell", path: "provision/install-all.sh", privileged: false
end
