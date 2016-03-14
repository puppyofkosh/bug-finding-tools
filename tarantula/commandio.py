import subprocess

def get_output(command):
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    stdout, stderr = proc.communicate()

    if len(stderr) > 0:
        print "{0}".format(command)
        print stderr
        raise RuntimeError("Why did it write to stderr?")
    return stdout
