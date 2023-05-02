from pathlib import Path
from typing import List, Set, Dict, Tuple

from generator.core.ctrl.tsl_lib import TSLLib
from generator.core.ctrl.tsl_libfile_generator import TSLFileGenerator
from generator.core.model.tsl_extension import TSLExtension
from generator.core.tsl_config import config
from generator.expansions.tsl_translation_unit import TSLTranslationUnitContainer
from generator.utils.file_utils import strip_common_path_prefix, strip_path_prefix
from generator.utils.log_utils import LogInit


class TSLCMakeGenerator:
    @LogInit()
    def __init__(self):
        pass
    @staticmethod
    def generate_lib(lib: TSLLib, file_generator: TSLFileGenerator, translation_units: TSLTranslationUnitContainer, cmake_config: dict) -> None:
        def get_architecture_flags(lib: TSLLib) -> str:
            result: Set[str] = set()
            for primitive_definition in lib.primitive_class_set.definitions():
                extension: TSLExtension = lib.extension_set.get_extension_by_name(
                    primitive_definition.target_extension)
                if extension.data["needs_arch_flags"]:
                    arch_flags: dict = extension.data["arch_flags"] if "arch_flags" in extension.data else dict()
                    for flag in primitive_definition.architecture_flags:
                        f = flag
                        if flag in arch_flags:
                            f = arch_flags[flag]
                        result.add(f"{config.compiler_architecture_prefix}{f}")
            return " ".join(result)
        def get_warning_options() -> str:
            silent_warnings = " ".join(config.silent_warnings)
            app = ''
            if not config.emit_workaround_warnings:
                app = "no-"
            return f"{silent_warnings} -W{app}deprecated-declarations"

        header_files: List[Path] = [strip_common_path_prefix(hf.file_name, config.generation_out_path) for hf in file_generator.library_files]

        config.generation_out_path.joinpath("CMakeLists.txt").write_text(
            config.get_template("expansions::cmake_lib").render(
                { **cmake_config,
                    **{
                        "header_files": header_files,
                        "library_root_path": f"{strip_common_path_prefix(config.lib_root_path, config.generation_out_path)}/",
                        "tsl_target_compile_options": f"{get_architecture_flags(lib)} {get_warning_options()} -flax-vector-conversions",
                        "use_concepts": config.use_concepts,
                        "subdirectories": [strip_common_path_prefix(path, config.generation_out_path) for path, translation_units in translation_units.translation_units]
                    }
                }
            )
        )
        print("To use TSL, apply the following changes:")
        print(f"   CMakeLists.txt (top-level):                 add_subdirectory({strip_path_prefix(config.generation_out_path)})")
        print(f"                                               target_link_libraries(<target> tsl)")
        print(f"   C++ Source/Header file which uses TSL:      #include <{strip_common_path_prefix(config.lib_root_header, config.lib_root_path)}>")
        print(f"General usage:")
        print(f"   Using namespace declaration:                /*...*/ ")
        print(f"   (we generally discourage this               using namespace {config.lib_namespace};")
        print(f"    kind of usage)                             auto result = add<simd<uint64_t, sse>>(a, b);")
        print(f"                                               /*...*/")
        print(f"   Explicit usage:                             /*...*/ ")
        print(f"                                               auto result = {config.lib_namespace}::add<{config.lib_namespace}::simd<uint64_t, {config.lib_namespace}::sse>>(a, b);")
        print(f"                                               /*...*/ ")


    @staticmethod
    def generate_source_file(tus: TSLTranslationUnitContainer, cmake_config: dict) -> None:
        for path, translation_units in tus.translation_units:
            path.mkdir(parents=True, exist_ok=True)
            targets: Dict[str, Tuple[List[Path], List[Path]]] = {}
            for unit in translation_units:
                tup = ([strip_common_path_prefix(hf.file_name, path) for hf in unit.header_files],
                       [strip_common_path_prefix(sf.file_name, path) for sf in unit.source_files])
                targets[unit.target_name] = tup
            path.joinpath("CMakeLists.txt").write_text(
                config.get_template("expansions::cmake").render(
                    {
                        **cmake_config,
                        **{
                            "targets": targets
                        }
                    }
                )
            )