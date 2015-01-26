# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "chef/debian-6.0.8"
  config.vm.network "forwarded_port", guest: 8000, host: 8001
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.synced_folder '.', '/vagrant', nfs: true

  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--cpus", "1"]
    vb.customize ["modifyvm", :id, "--memory", "1024"]
  end
end