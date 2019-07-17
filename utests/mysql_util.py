import subprocess

def mysqldump(out_path):
    with open(out_path, 'wb') as fob:
        called_proc = subprocess.run(['mysqldump'],
            stdout=fob, stderr=subprocess.DEVNULL)
    return not called_proc.returncode

def ensure_mysql_running():
    if not is_mysql_running():
        start_mysql()

def is_mysql_running():
    called_proc = subprocess.run(['service', 'mysql', 'status'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return not called_proc.returncode

def start_mysql():
    called_proc = subprocess.run(['service', 'mysql', 'start'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return not called_proc.returncode
    
def stop_mysql():
    called_proc = subprocess.run(['systemctl', 'mysql', 'stop'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return not called_proc.returncode

def mysql_execute(command):
    command = command.encode('utf-8')
    called_proc = subprocess.run(['mysql', '-u', 'root'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, input=command)
    return not called_proc.returncode

def mysql_execute_file(path):
    with open(path, 'rb') as fob:
        data = fob.read()
    called_proc = subprocess.run(['mysql', '-u', 'root'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, input=data)
    return not called_proc.returncode
