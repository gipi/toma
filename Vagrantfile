# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.share_folder "salt_file_root", "/srv/salt", Dir.pwd + '/salt'
  config.vm.box = "debian-squeeze"
  config.vm.box_url = "http://mathie-vagrant-boxes.s3.amazonaws.com/debian_squeeze_32.box"

  config.vm.provision :salt do |salt|
    salt.minion_config = Dir.pwd + "/salt/minion.conf"
    salt.run_highstate = true
    salt.salt_install_type = "stable"
  end
end
