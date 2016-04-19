import argparse

import feature_computer
import projects

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", help="Name of project")
    args = parser.parse_args()


    if args.project_name == "all":
        for p in projects.get_siemens_projects():
            print(p)
            feature_computer.compute_features(p)
    else:
        feature_computer.compute_features(args.project_name)


if __name__ == "__main__":
    main()
