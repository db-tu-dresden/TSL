# https://stackoverflow.com/a/377028
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ.get("PATH", "").split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def get_compile_info_from_compiler(compiler: str, arch_string: str):
    import subprocess, re, platform
    info = ""
    if "clang" in compiler:
        ps = subprocess.Popen(("clang", "-E", "-", arch_string, "-###"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info = ps.stderr.read().decode("utf-8")
        return(re.findall(r'"-target-feature" "\+([^\"]+)"', info))
    elif "g++" in compiler:
        ps = subprocess.Popen(("g++", "-E", "-", arch_string, "-###"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info = ps.stderr.read().decode("utf-8")
        return(re.findall(r' -m((?!no-)[^\s]+)', info))

def get_compile_info_from_lscpu():
    import subprocess, re, os
    if which("lscpu"):
        my_env = os.environ.copy()
        my_env["LANG"] = "en"
        ps = subprocess.Popen(("lscpu"), env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info2 = ps.stderr.read()
        info = ps.stdout.read()
        lines = info.decode("utf-8").split("\n")
        
        regex = re.compile(r"\s*Flags:\s*(?P<flags>(\w+\s)*(\w+))")
        flags_set = set()
        for line in lines:
            if line.lstrip().lower().startswith("flags"):
                for _, match in enumerate(regex.finditer(line)):
                    for flag in match.group("flags").split(" "):
                        flags_set.add(flag)
        return flags_set
    else:
        print("No LSCPU")
        return set()

def get_platform():
    import platform
    if "Darwin" in platform.system():
        return "Apple"
    else:
        return platform.system()

import platform
arch = platform.uname()[4]
# if "x86" in arch:
#     print(f"x86 CPU on {get_platform()}")
#     arch_string = "-march=native"
# elif "aarch" in arch or "Apple" in get_platform():
#     print("ARM CPU or Apple System")

flags = set()

if which("lscpu"):
    flags = get_compile_info_from_lscpu()
else:
    
    arch_string = ""
    if "Apple" in get_platform() or "aarch" in arch:
        arch_string = "-mcpu=native"
    else:
        arch_string = "-march=native"
    
    print("Debug:", arch, get_platform())
    gcc_flags = get_compile_info_from_compiler("g++", "-march=native") if which("g++") else set()
    clang_flags = get_compile_info_from_compiler("clang", arch_string) if which("clang") else set()
    flags = gcc_flags + clang_flags
    
print(' '.join(sorted(flags)))