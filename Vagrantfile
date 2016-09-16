# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "boxcutter/ubuntu1604"

    config.vm.network "forwarded_port", guest: 8000, host: 8000

    # Required for NFS to work, pick any local IP
    config.vm.network :private_network, ip: '192.168.50.50'
    # Use NFS for shared folders for better performance
    config.vm.synced_folder '.', '/home/vagrant/ajapaik-web', nfs: true

    config.vm.provider "virtualbox" do |v|
        host = RbConfig::CONFIG['host_os']

        # Give VM 1/4 system memory
        if host =~ /darwin/
            # sysctl returns Bytes and we need to convert to MB
            mem = `sysctl -n hw.memsize`.to_i / 1024
        elsif host =~ /linux/
            # meminfo shows KB and we need to convert to MB
            mem = `grep 'MemTotal' /proc/meminfo | sed -e 's/MemTotal://' -e 's/ kB//'`.to_i
        elsif host =~ /mswin|mingw|cygwin/
            # Windows code via https://github.com/rdsubhas/vagrant-faster
            mem = `wmic computersystem Get TotalPhysicalMemory`.split[1].to_i / 1024
        end

        mem = mem / 1024 / 4
        v.customize ["modifyvm", :id, "--memory", mem]
    end
end
