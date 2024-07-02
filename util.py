import os
import signal
import subprocess

HOST = os.environ.get('HOST')


def close_ports(ports):
    for port in ports:
        try:
            # Find the process using the port
            command = f'netstat -ano | findstr {HOST}:{port}'
            output = subprocess.check_output(command, shell=True).decode()
            lines = output.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    pid = line.rstrip().split()[-1]
                    os.kill(int(pid), signal.SIGTERM)
        except Exception as e:
            pass