import os
import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage {0} project version".format(sys.argv[0]))

    proj = sys.argv[1]
    version = sys.argv[2]

    working = os.path.join("programs", proj, "source.alt", "source.orig", "*.c")
    buggy = os.path.join("programs", proj, "versions.alt", "versions.orig", version, "*.c")
    os.system("diff {0} {1}".format(working, buggy))
