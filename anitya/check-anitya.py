#!/usr/bin/python3

import requests
import subprocess
import tabulate
import termstyle

PROGRAMS = [
    (6700, 'tcpflow'),
    (16892, 'ddrescueview'),
    (1330, 'html-xml-utils'),
    (16891, 'fred'),
    (16890, 'H2rename'),
    (16889, 'chntpw'),
    ]

def main():
    versions = []
    for prog_id, prog_name in PROGRAMS:
        res = requests.get('https://release-monitoring.org/project/%d/' % prog_id)
        res.raise_for_status()
        lines = res.text.splitlines()
        max_version = None
        for line in lines:
            if "doap:revision" in line:
                version = line[line.find('>')+1:line.rfind('<')].split('.')
                if max_version is None or version > max_version:
                    max_version = version
        res = subprocess.run(['zypper', 'if', prog_name], stdout=subprocess.PIPE)
        for line in res.stdout.splitlines():
            if line.startswith(b'Version'):
                opensuse_version = line[line.find(b':')+2:line.find(b'-')].decode().split('.')
                break
        versions.append((prog_name, '.'.join(max_version), '.'.join(opensuse_version)))
    print(tabulate.tabulate(versions, headers=('name', 'anitya', 'opensuse')))

if __name__ == '__main__':
    main()
