import os, shlex, subprocess 
from subprocess import Popen, run
from utils import *
from datetime import datetime

def build_mcperf_on_agent():
    agent_ip = get_external_ip("agent")
    build_mcperf_on_remote(agent_ip)

def build_mcperf_on_measure():
    measure_ip = get_external_ip("measure")
    build_mcperf_on_remote(measure_ip)

def build_mcperf():
    build_mcperf_on_agent()
    build_mcperf_on_measure()

def run_experiment_1():
    agent_ip = get_external_ip("agent")
    p_agent = run_remote_command(agent_ip, f"{MCPATH} -T 8 -A", False)

    measure_ip = get_external_ip("measure")
    agent_internal_ip = get_internal_ip("agent")
    memcached_ip = get_memcached_ip()

    run_remote_command(measure_ip, f"{MCPATH} -s {memcached_ip} --loadonly")
    p_measure = run_remote_command(measure_ip, f"{MCPATH} -s {memcached_ip} -a {agent_internal_ip} --noload -T 8 -C 8 -D 4 -Q 1000 -c 8 -t 5 -w 2 --scan 5000:80000:5000", False)

    measure_output, measure_error = p_measure.communicate()
    p_agent.kill()
    agent_output, agent_error = p_agent.communicate()

    output_path = f"logs/{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}/"
    output_path_measure = os.path.join(output_path, "measure.txt")
    output_path_agent = os.path.join(output_path, "agent.txt")
    os.makedirs(os.path.dirname(output_path_measure), exist_ok=True)

    with open(output_path_measure, "w") as f:
        f.write(measure_output)
        if measure_error is not None:
            f.write(measure_error)
    with open(output_path_agent, "w") as f:
        f.write(agent_output)
        if agent_error is not None:
            f.write(agent_error)

def setup_memcached():
    command_line = "/bin/bash ./scripts/part1/launch_memcached.sh"
    run(shlex.split(command_line), stdout=subprocess.PIPE)

def setup_cluster():
    command_line = "/bin/bash ./scripts/part1/launch_cluster.sh"
    run(shlex.split(command_line), stdout=subprocess.PIPE)

def cleanup():
    command_line = "kops delete cluster part1.k8s.local --yes"
    args = shlex.split(command_line)
    run(args)

def main():
    setup_cluster()
    setup_memcached()
    build_mcperf()

    # run_experiment_1()

    # cleanup()

if __name__ == "__main__":
    main()
