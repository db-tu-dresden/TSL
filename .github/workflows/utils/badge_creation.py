import argparse
import json
import sys

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Generate outcome for the generation step')
  parser.add_argument('--git-sha', help="Git SHA", required=True, type=str, dest='git_sha')
  parser.add_argument('step', choices=['generation', 'testing-x86', 'testing-aarch64', 'package-deb', 'package-rpm', 'release-tarball', 'release-ghpages'])
  args = parser.parse_args()
  
  if args.step == "generation":
    job_name_prefix = "run-generation"
    step_name = ["Generate tsl"]
  elif args.step == "testing-x86":
    job_name_prefix = "run-compile-and-test-x86"
    step_name = ["Run Tests"]
  elif args.step == "testing-aarch64":
    job_name_prefix = "run-compile-and-test-aarch64"
    step_name = ["Run Tests"]
  elif args.step == "package-deb":
    job_name_prefix = "package-deb"
    step_name = ["Run dpkb-buildpackage", "Test install", "Check install directory", "Compile test programm", "Test uninstall", "Upload release artifacts"]
  elif args.step == "package-rpm":
    job_name_prefix = "package-rpm"
    step_name = ["Run rpmbuild", "Test install", "Check install directory", "Compile test programm", "Test uninstall", "Upload release artifacts"]
  elif args.step == "release-tarball":
    job_name_prefix = "create-release"
    step_name = ["Copy setup_tsl.sh", "Create Release"]
  elif args.step == "release-ghpages":
    job_name_prefix = "deploy-ghpages"
    step_name = ["Setup Pages", "Upload artifact", "Deploy to GitHub Pages"]
  
  data_in = sys.stdin.read()  
  data = json.loads(data_in)
  success = []
  for job in data["jobs"]:
    job_git_sha = job.get("head_sha", "<unknown>")
    if job_git_sha == args.git_sha:
      name = job.get("name", "<unknown>")
      if name.startswith(job_name_prefix):
        success.append(job['conclusion'] == "success")
        print(f"{name}: {job['conclusion']}", file=sys.stderr)
        for step in job["steps"]: 
          if step["name"] in step_name:
            success.append(step["conclusion"] == "success")
            print(f"{name} ({step['name']}): {step['conclusion']}", file=sys.stderr)
  if all(success):
    exit(0)
  else:
    exit(1)