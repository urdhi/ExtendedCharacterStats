#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
import re

'''
This program accepts one optional command line option:

release If provided this will create release ready ZIP files

        Default: 'False'

'''
addonDir = 'ExtendedCharacterStats'
isReleaseBuild = False


def main():
    global isReleaseBuild
    if len(sys.argv) > 1:
        isReleaseBuild = sys.argv[1]
        print("Creating a release build")

    version_dir = get_version_dir(isReleaseBuild)

    if os.path.isdir('releases/%s' % version_dir):
        print("Warning: Folder already exists, removing!")
        shutil.rmtree('releases/%s' % version_dir)

    release_folder_path = 'releases/%s' % version_dir
    release_addon_folder_path = release_folder_path + ('/%s' % addonDir)

    copy_content_to(release_addon_folder_path)

    zip_name = '%s-%s' % (addonDir, version_dir)
    zip_release_folder(zip_name, version_dir, addonDir)

    interface_version = get_interface_version()

    with open(release_folder_path + '/release.json', 'w') as rf:
        rf.write('''{
    "releases": [
        {
            "filename": "%(z)s.zip",
            "nolib": false,
            "metadata": [
                {
                    "flavor": "classic",
                    "interface": %(s)s
                },
                {
                    "flavor": "bcc",
                    "interface": %(s)s
                },
                {
                    "flavor": "wrath",
                    "interface": %(s)s
                }
            ]
        }
    ]
}''' % ({'z': zip_name, 's': interface_version}))

    print('New release "%s" created successfully' % version_dir)


def get_version_dir(is_release_build):
    version, nr_of_commits, recent_commit = get_git_information()
    print("Tag: " + version)
    if is_release_build:
        version_dir = "%s" % version
    else:
        version_dir = "%s-%s" % (version, recent_commit)

    print("Number of commits since tag: " + nr_of_commits)
    print("Most Recent commit: " + recent_commit)
    branch = get_branch()
    if branch != "master":
        version_dir += "-%s" % branch
    print("Current branch: " + branch)

    return version_dir


directoriesToSkip = ['.git', '.github', '.history', '.idea', 'releases']
filesToSkip = ['.gitattributes', '.gitignore', '.luacheckrc', 'build.py', 'changelog.py', 'lua-style.config']


def copy_content_to(release_folder_path):
    for _, directories, files in os.walk('.'):
        for directory in directories:
            if directory not in directoriesToSkip:
                shutil.copytree(directory, '%s/%s' % (release_folder_path, directory))
        for file in files:
            if file not in filesToSkip:
                shutil.copy2(file, '%s/%s' % (release_folder_path, file))
        break


def zip_release_folder(zip_name, version_dir, addon_dir):
    root = os.getcwd()
    os.chdir('releases/%s' % version_dir)
    shutil.make_archive(zip_name, "zip", ".", addon_dir)
    os.chdir(root)


def get_git_information():
    if is_tool("git"):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        p = subprocess.check_output(["git", "describe", "--tags", "--long"], cwd=script_dir, stderr=subprocess.STDOUT)
        tag_string = str(p).rstrip("\\n'").lstrip("b'")

        # versiontag (v4.1.1) from git, number of additional commits on top of the tagged object and most recent commit.
        version_tag, nr_of_commits, recent_commit = tag_string.rsplit("-", maxsplit=2)
        recent_commit = recent_commit.lstrip("g")  # There is a "g" before all the commits.
        return version_tag, nr_of_commits, recent_commit
    else:
        raise RuntimeError("Warning: Git not found on the computer, using fallback to get a version.")


def get_branch():
    if is_tool("git"):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # git rev-parse --abbrev-ref HEAD
        p = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=script_dir)
        branch = str(p).rstrip("\\n'").lstrip("b'")
        return branch


def get_interface_version():
    with open('ExtendedCharacterStats-Classic.toc', 'r') as toc:
        return re.match('## Interface: (.*?)\n', toc.read(), re.DOTALL).group(1)


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    return shutil.which(name) is not None


if __name__ == "__main__":
    main()
