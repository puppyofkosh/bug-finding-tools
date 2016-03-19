import subprocess



def get_output(args, use_shell=False):
    proc = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=use_shell)
    stdout, stderr = proc.communicate()

    if len(stderr) > 0:
        print("{0}".format(args))
        print(stderr)
        raise RuntimeError("Why did it write to stderr?")
    return stdout
