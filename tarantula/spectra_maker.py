import os

import test_runner
import run_result
import projects

SPECTRA_DIR = "spectra"
def get_spectra_file(project_name, version):
    return os.path.join(SPECTRA_DIR,
                        project_name + "-" + version + ".res")

def load_run_res(project_name, version):
    return run_result.load(get_spectra_file(project_name,
                                            version))

def make_spectra(project_name, projectdir, versions, remake):
    versions = list(versions)
    assert len(versions) > 0
    original_dir = os.getcwd()

    os.chdir(projectdir)
    project = projects.get_project(project_name, versions[0])
    test_runner.initialize_directory(project)
    runner = test_runner.TestRunner(project)

    runner.load_correct_outputs()
    os.chdir(original_dir)
    
    for v in versions:
        project = projects.get_project(project_name, v)
        outfile = get_spectra_file(project.name, project.version)

        exists = os.path.exists(outfile)
        if exists and not remake:
            print("Spectra already exists for {0}. Skipping".format(v))
            continue

        os.chdir(projectdir)
        print("Running version {0}".format(v))
        runner.set_project(project)

        run_to_result = runner.get_buggy_version_results()
        os.chdir(original_dir)

        if not os.path.exists(SPECTRA_DIR):
            os.mkdir(SPECTRA_DIR)

        outfile = get_spectra_file(project.name, project.version)
        print("Saving results to {0}".format(outfile))
        run_result.save(outfile, run_to_result)
