import os, shlex, subprocess

from subprocess import Popen, run

MCPATH = "/home/ubuntu/memcache-perf/mcperf"

def get_node_propetries(node_name):
    command_line = f"kubectl get nodes -o wide"
    args = shlex.split(command_line)

    # node_properties = subprocess.check_call(args, shell=True)
    kubectl_p = Popen(args, stdout=subprocess.PIPE)
    grep_p = Popen(shlex.split(f"grep {node_name}"), stdin=kubectl_p.stdout, stdout=subprocess.PIPE, universal_newlines=True)
    kubectl_p.stdout.close()
    node_properties, err_output = grep_p.communicate()
    return node_properties

def get_external_ip(node_name: str) -> str:
    node_properties = get_node_propetries(node_name)
    if node_properties == "":
        print(f"No IP was found for node named: {node_name}")
        raise ValueError(f"External IP not found for {node_name}")
    else:
        return node_properties.split()[6]

def get_internal_ip(node_name: str) -> str:
    node_properties = get_node_propetries(node_name)

    if node_properties == "":
        print(f"No IP was found for node named: {node_name}")
        raise ValueError(f"Internal IP not found for {node_name}")
    else:
        return node_properties.split()[5]

def get_memcached_ip() -> str:
    command_line = f"kubectl get pods -o wide"
    args = shlex.split(command_line)

    kubectl_p = Popen(args, stdout=subprocess.PIPE)
    grep_p = Popen(shlex.split(f"grep some-memcached"), stdin=kubectl_p.stdout, stdout=subprocess.PIPE, universal_newlines=True)
    kubectl_p.stdout.close()
    node_properties, err_output = grep_p.communicate()

    if node_properties == "":
        print(f"No IP was found for memcached pod")
        raise ValueError("IP not found for memcached")
    else:
        return node_properties.split()[5]

def run_remote_command(remote_ip, command_line, block=True):
    args = shlex.split(f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i ~/.ssh/cloud-computing ubuntu@{remote_ip} " + command_line) 
    if block:
        run(args, text=True)
    else:
        p = Popen(args, stdout=subprocess.PIPE, text=True)
        return p

def build_mcperf_on_remote(server_ip: str):
    copy_command = f"scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i ~/.ssh/cloud-computing scripts/part1/compile_mcperf.sh ubuntu@{server_ip}:~/"
    scp_p = run(shlex.split(copy_command))
    run_remote_command(server_ip, "/bin/bash ~/compile_mcperf.sh")


