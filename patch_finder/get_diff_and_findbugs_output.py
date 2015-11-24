import os

# Find all the patches, so I can look at them.

version = "5"
proj = "Time"

os.system("export PATH=$PATH:~/bug-finding/defects4j/framework/bin")

os.system("defects4j checkout -p {0} -v {1}b -w current_proj/".format(proj, version))
os.system("defects4j checkout -p {0} -v {1}f -w current_fixed_proj/".format(proj, version))

src_dir = "src"
if src_dir not in os.listdir("current_proj"):
    src_dir = "source"

os.system("git diff current_proj/{0}/ current_fixed_proj/{0}/ > output/{1}_diff.txt".format(src_dir, version))

# Run findbugs. It looks at bytecode so we have to compile the project
os.chdir("current_proj")
os.system("defects4j compile")
os.chdir("..")

build_dir = "build"
if build_dir not in os.listdir("current_proj"):
    build_dir = "target"


os.system("echo current_proj/{0} > findbugs_input_file".format(build_dir))
os.system("findbugs -textui -analyzeFromFile findbugs_input_file -output output/findbugs_output_{0}.txt -sortByClass".format(version))
