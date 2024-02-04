#Beegfs server setup for Linux(RHEL,ROCKY)
#Author : Amogha-Reddy
#email : amoghareddy39@gmail.com

import pytest
import yaml
from testinfra import get_host

def load_user_config(file_path):
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)
    return config

def run_command_and_get_output(host, command):
    result = host.run(command)
    return result

def remove_old_beegfs(host):
    commands = [
        "dnf remove beegfs-mgmtd beegfs-meta libbeegfs-ib beegfs-storage -y",
        "rm -rf /etc/beegfs",
        "rm -rf /opt/beegfs",
        "rm -rf /data/beegfs",
        "rm -rf /mnt/myraid1"
    ]
    for command in commands:
        result = run_command_and_get_output(host, command)
        assert result.rc == 0, f"Failed to execute command: {command}. Error: {result.stderr}"
    print("Removal of old BeeGFS installation was successful.")

def install_beegfs_repo(host, version):
    repo_url = f"https://www.beegfs.io/release/beegfs_{version}/dists/beegfs-rhel8.repo"
    command = f"curl -o /etc/yum.repos.d/beegfs_rhel8.repo {repo_url}"
    result = run_command_and_get_output(host, command)
    assert result.rc == 0, f"Failed to install BeeGFS repository. Error: {result.stderr}"
    print(f"Installation of BeeGFS repository {version} was successful.")

def install_beegfs_packages(host):
    command = "yum install beegfs-mgmtd beegfs-meta libbeegfs-ib beegfs-storage -y"
    result = run_command_and_get_output(host, command)
    assert result.rc == 0, f"Failed to install BeeGFS packages. Error: {result.stderr}"
    print("Installation of BeeGFS packages was successful.")

def update_beegfs_config_files(host, beegfs_server_ip):
    commands = [
        f"/opt/beegfs/sbin/beegfs-setup-mgmtd -p /data/beegfs/beegfs_mgmtd",
        f"/opt/beegfs/sbin/beegfs-setup-meta -p /data/beegfs/beegfs_meta -s 2 -m {beegfs_server_ip}",
        f"/opt/beegfs/sbin/beegfs-setup-storage -p /mnt/myraid1/beegfs_storage -s 3 -i 301 -m {beegfs_server_ip}"
    ]
    for command in commands:
        result = run_command_and_get_output(host, command)
        assert result.rc == 0, f"Failed to execute command: {command}. Error: {result.stderr}"
    print("Update of BeeGFS config files was successful.")

def get_connauthfile(host):
    command = "dd if=/dev/random of=/etc/beegfs/connauthfile bs=128 count=1"
    result = run_command_and_get_output(host, command)
    assert result.rc == 0, f"Failed to execute command: {command}. Error: {result.stderr}"
    print("Creation of connauthfile was successful.")

def update_connAuthFile_values(host):
    steps = [
        f"sed -i 's/^connAuthFile\s*=\s*$/connAuthFile                 = \/etc\/beegfs\/connauthfile/' /etc/beegfs/beegfs-meta.conf",
        f"sed -i 's/^connAuthFile\s*=\s*$/connAuthFile                 = \/etc\/beegfs\/connauthfile/' /etc/beegfs/beegfs-mgmtd.conf",
        f"sed -i 's/^connAuthFile\s*=\s*$/connAuthFile                 = \/etc\/beegfs\/connauthfile/' /etc/beegfs/beegfs-storage.conf"
    ]
    for step in steps:
        result = run_command_and_get_output(host, step)
        assert result.rc == 0, f"Failed to execute command: {step}. Error: {result.stderr}"
    print("Update of connAuthFile variable was updated successful.")

def start_beegfs_services(host):
    commands = [
        "systemctl start beegfs-meta",
        "systemctl start beegfs-mgmtd",
        "systemctl start beegfs-storage"
    ]
    for command in commands:
        result = run_command_and_get_output(host, command)
        assert result.rc == 0, f"Failed to execute command: {command}. Error: {result.stderr}"
    print("Update of BeeGFS config files was successful.")

def configure_and_reload_firewall(host):
    commands = [
        "systemctl start firewalld",
        "firewall-cmd --permanent --zone=public --add-port=8008/tcp",
        "firewall-cmd --permanent --zone=public --add-port=8008/udp",
        "firewall-cmd --permanent --zone=public --add-port=8005/tcp",
        "firewall-cmd --permanent --zone=public --add-port=8005/udp",
        "firewall-cmd --permanent --zone=public --add-port=8003/udp",
        "firewall-cmd --permanent --zone=public --add-port=8003/tcp",
        "firewall-cmd --permanent --zone=public --add-port=8004/udp",
        "firewall-cmd --permanent --zone=public --add-port=8004/tcp",
        "firewall-cmd --permanent --zone=public --add-port=8006/tcp",
        "firewall-cmd --reload"
    ]
    for command in commands:
        result = run_command_and_get_output(host, command)
        assert result.rc == 0, f"Failed to execute command: {command}. Error: {result.stderr}"
    print("Firewall configuration and reload was successful.")

def test_install_beegfs(host):
    # provide your input via setup_beegfs_mgmt_config.yml and specify the path to file
    
    user_config_file_path = "/root/setup_beegfs_mgmt_config.yml"  
    user_config = load_user_config(user_config_file_path)

    # Remove old BeeGFS installation
    remove_old_beegfs(host)

    # Install BeeGFS repository
    install_beegfs_repo(host, user_config['beegfs_version'])

    # Install BeeGFS packages
    install_beegfs_packages(host)

    # Update BeeGFS config files
    update_beegfs_config_files(host, user_config['beegfs_server_ip'])

    # Get connauthfile
    get_connauthfile(host)

    # Update connAuth variable vaule
    update_connAuthFile_values(host)

    #start beegfs services
    start_beegfs_services(host)

    #configure and reload firewall
    configure_and_reload_firewall(host)

@pytest.fixture
def host(request):
    user_config_file_path = "/root/setup_beegfs_mgmt_config.yml"  # provide your input via setup_beegfs_mgmt_config file and specify the path to file 
    user_config = load_user_config(user_config_file_path)
    host = get_host(f"ssh://{user_config['username']}@{user_config['ip']}")
    return host
