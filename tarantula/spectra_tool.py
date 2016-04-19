import argparse

import projects
import spectra_maker


#
# This tool will make all the spectra for a given project
#
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", help="Name of project")
    parser.add_argument("project_dir", help="Location of project dir")
    args = parser.parse_args()
    
    spectra_maker.make_spectra(args.project_name,
                               args.project_dir,
                               projects.get_version_names(args.project_name),
                               False)

if __name__ == "__main__":
    main()
