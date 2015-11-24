import os

# Find all the patches, so I can look at them.

proj = "Math"

os.system("export PATH=$PATH:~/bug-finding/defects4j/framework/bin")
for i in range(1,107):
    filename = "{0}.txt".format(i)
    dest_dir = "patches/{0}".format(proj)
    if filename in os.listdir(dest_dir):
        continue


    os.system("defects4j checkout -p {0} -v {1}b -w current_proj/".format(proj, i))
    os.system("defects4j checkout -p {0} -v {1}f -w current_fixed_proj/".format(proj, i))

    src_dir = "src"
    if src_dir not in os.listdir("current_proj"):
        src_dir = "source"

    os.system("git diff current_proj/{0}/ current_fixed_proj/{0}/ > {1}/{2}".format(src_dir, dest_dir, filename))
