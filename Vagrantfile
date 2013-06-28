# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.synced_folder  Dir.pwd + '/salt', "/srv/salt"
  config.vm.box = "debian-squeeze"
  config.vm.box_url = "http://mathie-vagrant-boxes.s3.amazonaws.com/debian_squeeze_32.box"
  config.vm.network :public_network

  config.vm.provision :salt do |salt|
    salt.minion_config = Dir.pwd + "/salt/minion.conf"
    salt.run_highstate = true
    salt.salt_install_type = "stable"
  end
end
