# TSL Primitive Data
< Insert general remarks here >

## Basics
< Describe the basics here: how is it used within the generator, ...>

## Extension
< Describe what an extension is, what it represents >

### Fields
<a name="toc-extension"></a>
##### Table of Contents

|Required Fields|Optional Fields
|:--|:--|
[extension_name](#extension--extension_name) | [arch_flags](#extension--arch_flags)
[lscpu_flags](#extension--lscpu_flags) | [custom_types](#extension--custom_types)
[simdT_mask_type](#extension--simdT_mask_type) | [description](#extension--description)
[simdT_name](#extension--simdT_name) | [includes](#extension--includes)
[simdT_register_type](#extension--simdT_register_type) | [intrin_tp](#extension--intrin_tp)
[vendor](#extension--vendor) | [intrin_tp_full](#extension--intrin_tp_full)
[name](#extension-custom_types-entry_type--name) | [language](#extension--language)
[struct_code](#extension-custom_types-entry_type--struct_code) | [needs_arch_flags](#extension--needs_arch_flags)
[cmakelists_path](#extension-required_supplementary_libraries-entry_type--cmakelists_path) | [required_supplementary_libraries](#extension--required_supplementary_libraries)
[library_create_function](#extension-required_supplementary_libraries-entry_type--library_create_function) | [simdT_default_size_in_bits](#extension--simdT_default_size_in_bits)
[name](#extension-required_supplementary_libraries-entry_type--name) | [simdT_integral_mask_type](#extension--simdT_integral_mask_type)
 | [simdT_mask_type_attributes](#extension--simdT_mask_type_attributes)
 | [simdT_mask_type_compiler_attributes](#extension--simdT_mask_type_compiler_attributes)
 | [simdT_register_type_attributes](#extension--simdT_register_type_attributes)
 | [simdT_register_type_compiler_attributes](#extension--simdT_register_type_compiler_attributes)

<details>
<summary><a name="extension--extension_name"></a>extension_name: (required)</summary>

<blockquote>

type: `str` <br />
brief: Extension Name (used as filename). <br />
example: `'avx512'` <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--lscpu_flags"></a>lscpu_flags: (required)</summary>

<blockquote>

type: `list` <br />
entry_type: str <br />
brief: List of extension specific flags, exposed by using lscpu. <br />
example: `[ 'avx512cd', 'avx512f' ]` <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--simdT_mask_type"></a>simdT_mask_type: (required)</summary>

<blockquote>

type: `str` <br />
brief: Mask type, depending on the base type. <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--simdT_name"></a>simdT_name: (required)</summary>

<blockquote>

type: `str` <br />
brief: Extension Name which will be used inside the TSL. <br />
example: `'avx512'` <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--simdT_register_type"></a>simdT_register_type: (required)</summary>

<blockquote>

type: `str` <br />
brief: Vector register type, depending on the base type. <br />
example: `BaseType` <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--vendor"></a>vendor: (required)</summary>

<blockquote>

type: `str` <br />
brief: Vendor Name. <br />
example: `'intel'` <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--arch_flags"></a>arch_flags: (optional)</summary>

<blockquote>

type: `dict` <br />
brief: Dictionary for mapping architecture flags to compiler related arcitecture flags. Only non-obvious mappings must be included in this dictionary. <br />
example: `{sse4_1: 'msse4.1', sse4_2: 'msse4.2'}` <br />
default: {} <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--custom_types"></a>custom_types: (optional)</summary>

<blockquote>

type: `list` <br />
<details open>
<summary><a name="entry_type"></a>entry_type</summary>

<blockquote>

<details open>
<summary><a name="extension-custom_types-entry_type--name"></a>name: (required)</summary>

<blockquote>

type: `str` <br />
brief: Name of custom type. <br />
example: `gpu_reg_t` <br />


</blockquote>
</details>

<details open>
<summary><a name="extension-custom_types-entry_type--struct_code"></a>struct_code: (required)</summary>

<blockquote>

type: `str` <br />
brief: Implementation code for custom type struct. <br />


</blockquote>
</details>



</blockquote>
</details>

brief: List of custom types. <br />
default: [] <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--description"></a>description: (optional)</summary>

<blockquote>

type: `str` <br />
brief: A description of the SIMD extension which is used for doxygen generation. <br />
default: todo. <br />
recommended: True <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--includes"></a>includes: (optional)</summary>

<blockquote>

type: `list` <br />
default: [] <br />
entry_type: str <br />
brief: A list of includes which are required. <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--intrin_tp"></a>intrin_tp: (optional)</summary>

<blockquote>

type: `dict` <br />
brief: If intrinsics follow a specific pattern (for instance by enconding type informations into intrinsic-names), this can be used to generate multiple primitivies. <br />
example: `{uint8_t: ['u', '8'], uint16_t: ['u', '16']}. Usage: vaddq_{{ intrin_tp[ctype][0] }}{{ intrin_tp[ctype][1] }}` <br />
default: {} <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--intrin_tp_full"></a>intrin_tp_full: (optional)</summary>

<blockquote>

type: `dict` <br />
brief: If intrinsics follow a specific pattern (for instance by enconding type informations into intrinsic-names), this can be used to generate multiple primitivies. <br />
example: `{uint8_t: ['u', '8'], uint16_t: ['u', '16']}. Usage: vaddq_{{ intrin_tp_full[ctype] }}` <br />
default: {} <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--language"></a>language: (optional)</summary>

<blockquote>

type: `str` <br />
brief: Language string used by cmake. <br />
default: CXX <br />
example: `'CXX' or 'CUDA'` <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--needs_arch_flags"></a>needs_arch_flags: (optional)</summary>

<blockquote>

type: `bool` <br />
brief: Indicates, whether the lscpu-flags should be used as compiler flags. <br />
default: True <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--required_supplementary_libraries"></a>required_supplementary_libraries: (optional)</summary>

<blockquote>

type: `list` <br />
brief: List of libraries which are required for this extension. <br />
default: [] <br />
<details open>
<summary><a name="entry_type"></a>entry_type</summary>

<blockquote>

<details open>
<summary><a name="extension-required_supplementary_libraries-entry_type--cmakelists_path"></a>cmakelists_path: (required)</summary>

<blockquote>

type: `str` <br />
brief: Path to the top-level directory where the CMakeLists.txt file resides which will be used for add_subdirectory. <br />


</blockquote>
</details>

<details open>
<summary><a name="extension-required_supplementary_libraries-entry_type--library_create_function"></a>library_create_function: (required)</summary>

<blockquote>

type: `str` <br />
brief: Name of the function which will be used to create the library. <br />


</blockquote>
</details>

<details open>
<summary><a name="extension-required_supplementary_libraries-entry_type--name"></a>name: (required)</summary>

<blockquote>

type: `str` <br />
brief: Name of the library which will be used for linking. <br />


</blockquote>
</details>



</blockquote>
</details>



</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--simdT_default_size_in_bits"></a>simdT_default_size_in_bits: (optional)</summary>

<blockquote>

type: `int` <br />
brief: Default size of a vector register for the specific extension in bits. <br />
default: 0 <br />
example: `512` <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--simdT_integral_mask_type"></a>simdT_integral_mask_type: (optional)</summary>

<blockquote>

type: `str` <br />
brief: Integral type for a mask. This may differ from the mask_type. <br />
default: mask_t <br />
requirement: optional <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--simdT_mask_type_attributes"></a>simdT_mask_type_attributes: (optional)</summary>

<blockquote>

type: `str` <br />
brief: Additional attributes of mask type. <br />
example: `__attribute__((vector_size(64), __may_alias__, _aligned_(64)))` <br />
default: "" <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--simdT_mask_type_compiler_attributes"></a>simdT_mask_type_compiler_attributes: (optional)</summary>

<blockquote>

type: `str` <br />
brief: Additional attributes of mask type. <br />
example: `__attribute__((register))` <br />
default: "" <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--simdT_register_type_attributes"></a>simdT_register_type_attributes: (optional)</summary>

<blockquote>

type: `str` <br />
brief: Additional attributes of vector type. <br />
example: `__attribute__((vector_size(64), __may_alias__, _aligned_(64)))` <br />
default: "" <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>

<details>
<summary><a name="extension--simdT_register_type_compiler_attributes"></a>simdT_register_type_compiler_attributes: (optional)</summary>

<blockquote>

type: `str` <br />
brief: Additional attributes of vector type. <br />
example: `__attribute__((register))` <br />
default: "" <br />


</blockquote>

[Back to Table of Content](#toc-extension)

</details>



## Primitive
< Describe what a primitive is, what it represents >

### Fields
<a name="toc-primitive"></a>
##### Table of Contents
|Required Fields|Optional Fields
|:--|:--|
[primitive_name](#primitive--primitive_name) | [additional_non_specialized_template_parameters](#primitive--additional_non_specialized_template_parameters)
[ctype](#primitive-additional_non_specialized_template_parameters-entry_type--ctype) | [default_value](#primitive-additional_non_specialized_template_parameters-entry_type--default_value)
[name](#primitive-additional_non_specialized_template_parameters-entry_type--name) | [additional_simd_template_parameter](#primitive--additional_simd_template_parameter)
[name](#primitive-additional_simd_template_parameter-entry_type--name) | [default_value](#primitive-additional_simd_template_parameter-entry_type--default_value)
[ctype](#primitive-definitions-entry_type--ctype) | [brief_description](#primitive--brief_description)
[implementation](#primitive-definitions-entry_type--implementation) | [definitions](#primitive--definitions)
[lscpu_flags](#primitive-definitions-entry_type--lscpu_flags) | [additional_simd_template_base_type](#primitive-definitions-entry_type--additional_simd_template_base_type)
[target_extension](#primitive-definitions-entry_type--target_extension) | [additional_simd_template_base_type_mapping_dict](#primitive-definitions-entry_type--additional_simd_template_base_type_mapping_dict)
[ctype](#primitive-parameters-entry_type--ctype) | [additional_simd_template_extension](#primitive-definitions-entry_type--additional_simd_template_extension)
[name](#primitive-parameters-entry_type--name) | [includes](#primitive-definitions-entry_type--includes)
[ctype](#primitive-returns-entry_type--ctype) | [is_native](#primitive-definitions-entry_type--is_native)
[implementation](#primitive-testing-entry_type--implementation) | [specialization_comment](#primitive-definitions-entry_type--specialization_comment)
 | [vector_length_agnostic](#primitive-definitions-entry_type--vector_length_agnostic)
 | [vector_length_bits](#primitive-definitions-entry_type--vector_length_bits)
 | [detailed_description](#primitive--detailed_description)
 | [force_inline](#primitive--force_inline)
 | [functor_name](#primitive--functor_name)
 | [idof_name](#primitive--idof_name)
 | [includes](#primitive--includes)
 | [parameters](#primitive--parameters)
 | [attributes](#primitive-parameters-entry_type--attributes)
 | [declaration_attributes](#primitive-parameters-entry_type--declaration_attributes)
 | [default_value](#primitive-parameters-entry_type--default_value)
 | [description](#primitive-parameters-entry_type--description)
 | [is_parameter_pack](#primitive-parameters-entry_type--is_parameter_pack)
 | [returns](#primitive--returns)
 | [description](#primitive-returns-entry_type--description)
 | [test_function_name](#primitive--test_function_name)
 | [testing](#primitive--testing)
 | [implicitly_reliable](#primitive-testing-entry_type--implicitly_reliable)
 | [includes](#primitive-testing-entry_type--includes)
 | [requires](#primitive-testing-entry_type--requires)
 | [test_name](#primitive-testing-entry_type--test_name)
 | [tsl_implementation_namespace](#primitive--tsl_implementation_namespace)
 | [vector_name](#primitive--vector_name)
<details>
<summary><a name="primitive--primitive_name"></a>primitive_name: (required)</summary>

<blockquote>

type: `str` <br />
brief: Name of the primitive. <br />
example: `load` <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--additional_non_specialized_template_parameters"></a>additional_non_specialized_template_parameters: (optional)</summary>

<blockquote>

type: `list` <br />
<details open>
<summary><a name="entry_type"></a>entry_type</summary>

<blockquote>

<details open>
<summary><a name="primitive-additional_non_specialized_template_parameters-entry_type--ctype"></a>ctype: (required)</summary>

<blockquote>

type: `str` <br />
brief: Type of template. <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-additional_non_specialized_template_parameters-entry_type--name"></a>name: (required)</summary>

<blockquote>

type: `str` <br />
brief: Name of template parameter. <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-additional_non_specialized_template_parameters-entry_type--default_value"></a>default_value: (optional)</summary>

<blockquote>

type: `str` <br />
brief: A default value. <br />
default: "" <br />


</blockquote>
</details>



</blockquote>
</details>

default: [] <br />
brief: Additional template parameters which may be needed <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--additional_simd_template_parameter"></a>additional_simd_template_parameter: (optional)</summary>

<blockquote>

type: `dict` <br />
<details open>
<summary><a name="entry_type"></a>entry_type</summary>

<blockquote>

<details open>
<summary><a name="primitive-additional_simd_template_parameter-entry_type--name"></a>name: (required)</summary>

<blockquote>

type: `str` <br />
default: "" <br />
brief: Name of template parameter. <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-additional_simd_template_parameter-entry_type--default_value"></a>default_value: (optional)</summary>

<blockquote>

type: `str` <br />
default: "" <br />
brief: default value for the template parameter <br />


</blockquote>
</details>



</blockquote>
</details>

<details open>
<summary><a name="default"></a>default</summary>

<blockquote>

name: "" <br />
default_value: "" <br />


</blockquote>
</details>

brief: Additional template parameter which may be used for conversion operations. <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--brief_description"></a>brief_description: (optional)</summary>

<blockquote>

type: `str` <br />
default: todo. <br />
brief: Brief description of the primitive. <br />
recommended: True <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--definitions"></a>definitions: (optional)</summary>

<blockquote>

type: `list` <br />
default: [] <br />
<details open>
<summary><a name="entry_type"></a>entry_type</summary>

<blockquote>

<details open>
<summary><a name="primitive-definitions-entry_type--ctype"></a>ctype: (required)</summary>

<blockquote>

type: `list` <br />
entry_type: str <br />
brief: List of the C/C++ datatype(s) for which this definition is a specialization. If ctype == 'T', the specialization is base type agnostic. <br />
example: `['uint32_t', 'uint64_t'], ['uint64_t'], ['T']` <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-definitions-entry_type--implementation"></a>implementation: (required)</summary>

<blockquote>

type: `str` <br />
brief: The actual implementation for this definition. <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-definitions-entry_type--lscpu_flags"></a>lscpu_flags: (required)</summary>

<blockquote>

   same as: [lscpu_flags](#extension--lscpu_flags)


</blockquote>
</details>

<details open>
<summary><a name="primitive-definitions-entry_type--target_extension"></a>target_extension: (required)</summary>

<blockquote>

type: `list` <br />
entry_type: str <br />
brief: The TSL extension for which this definition is a specialization. <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-definitions-entry_type--additional_simd_template_base_type"></a>additional_simd_template_base_type: (optional)</summary>

<blockquote>

type: `list` <br />
entry_type: str <br />
default: [] <br />
brief: Return vector base type, which is used for conversion. <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-definitions-entry_type--additional_simd_template_base_type_mapping_dict"></a>additional_simd_template_base_type_mapping_dict: (optional)</summary>

<blockquote>

type: `dict` <br />
<details open>
<summary><a name="default"></a>default</summary>

<blockquote>



</blockquote>
</details>

brief: todo <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-definitions-entry_type--additional_simd_template_extension"></a>additional_simd_template_extension: (optional)</summary>

<blockquote>

type: `str` <br />
default: "" <br />
brief: Return vector extension, which is used for casts. <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-definitions-entry_type--includes"></a>includes: (optional)</summary>

<blockquote>

   same as: [includes](#extension--includes)


</blockquote>
</details>

<details open>
<summary><a name="primitive-definitions-entry_type--is_native"></a>is_native: (optional)</summary>

<blockquote>

type: `bool` <br />
default: True <br />
brief: A flag indicating whether the definition is using a 1-to-1 mapping (True) or whether it is some kind of a workaround (False). <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-definitions-entry_type--specialization_comment"></a>specialization_comment: (optional)</summary>

<blockquote>

type: `str` <br />
default: "" <br />
brief: Brief description of the primitive. <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-definitions-entry_type--vector_length_agnostic"></a>vector_length_agnostic: (optional)</summary>

<blockquote>

type: `bool` <br />
default: False <br />
brief: Indicates, whether a Primitive specialization is agnostic to the actual vector length (default: False). <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-definitions-entry_type--vector_length_bits"></a>vector_length_bits: (optional)</summary>

<blockquote>

type: `int` <br />
default: 0 <br />
brief: The size of a vector register for the specific extension in bits. (default: 0 indicates that the default amount of bits - defined for the extension - will be used). <br />


</blockquote>
</details>



</blockquote>
</details>

brief: A list of definitions for a specific primitive. <br />
recommended: True <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--detailed_description"></a>detailed_description: (optional)</summary>

<blockquote>

type: `str` <br />
default: todo. <br />
brief: Detailed description of the primitive. <br />
recommended: True <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--force_inline"></a>force_inline: (optional)</summary>

<blockquote>

type: `bool` <br />
default: True <br />
brief: A flag indicating whether the primitive should be marked as ((always_inline)). (default = True) <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--functor_name"></a>functor_name: (optional)</summary>

<blockquote>

type: `str` <br />
default: "" <br />
brief: Name for the functor class. This is used if multiple primitives exist with the same primitive name but with different parameters. <br />
example: `mask_load` <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--idof_name"></a>idof_name: (optional)</summary>

<blockquote>

type: `str` <br />
default: Idof <br />
brief: The template class name which is used to care about the implementation degree of freedom. <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--includes"></a>includes: (optional)</summary>

<blockquote>

   same as: [includes](#extension--includes)


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--parameters"></a>parameters: (optional)</summary>

<blockquote>

type: `list` <br />
default: [] <br />
<details open>
<summary><a name="entry_type"></a>entry_type</summary>

<blockquote>

<details open>
<summary><a name="primitive-parameters-entry_type--ctype"></a>ctype: (required)</summary>

<blockquote>

type: `str` <br />
brief: TSL type of the parameter with all cvref qualifiers. <br />
example: `Vec::vector_type const &` <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-parameters-entry_type--name"></a>name: (required)</summary>

<blockquote>

type: `str` <br />
brief: Name of the parameter. <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-parameters-entry_type--attributes"></a>attributes: (optional)</summary>

<blockquote>

type: `str` <br />
brief: Parameter attributes. <br />
example: `__restrict__` <br />
default: "" <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-parameters-entry_type--declaration_attributes"></a>declaration_attributes: (optional)</summary>

<blockquote>

type: `str` <br />
brief: Parameter declaration attributes <br />
example: `[[maybe_unused]]` <br />
default: "" <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-parameters-entry_type--default_value"></a>default_value: (optional)</summary>

<blockquote>

   same as: [default_value](#primitive-additional_non_specialized_template_parameters-entry_type--default_value)


</blockquote>
</details>

<details open>
<summary><a name="primitive-parameters-entry_type--description"></a>description: (optional)</summary>

<blockquote>

type: `str` <br />
brief: A short description of the parameter. <br />
default: todo. <br />
recommended: True <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-parameters-entry_type--is_parameter_pack"></a>is_parameter_pack: (optional)</summary>

<blockquote>

type: `bool` <br />
default: False <br />
brief: A flag indicating whether the definition is using a 1-to-1 mapping (True) or whether it is some kind of a workaround (False). <br />


</blockquote>
</details>



</blockquote>
</details>

brief: A list of necessary parameters for the primitive. <br />
example: `[{ctype: 'Vec::vector_type const &', name: 'a', description: 'first summand'}, {ctype: 'Vec::vector_type const &', name: 'b', description: 'second summand'}]` <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--returns"></a>returns: (optional)</summary>

<blockquote>

type: `dict` <br />
<details open>
<summary><a name="entry_type"></a>entry_type</summary>

<blockquote>

<details open>
<summary><a name="primitive-returns-entry_type--ctype"></a>ctype: (required)</summary>

<blockquote>

   same as: [ctype](#primitive-parameters-entry_type--ctype)


</blockquote>
</details>

<details open>
<summary><a name="primitive-returns-entry_type--description"></a>description: (optional)</summary>

<blockquote>

   same as: [description](#primitive-parameters-entry_type--description)


</blockquote>
</details>



</blockquote>
</details>

<details open>
<summary><a name="default"></a>default</summary>

<blockquote>

ctype: void <br />
description: "" <br />


</blockquote>
</details>

brief: The return type of the primitive. (default = void) <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--test_function_name"></a>test_function_name: (optional)</summary>

<blockquote>

type: `str` <br />
brief: @TODO <br />
example: `test_add` <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--testing"></a>testing: (optional)</summary>

<blockquote>

type: `list` <br />
<details open>
<summary><a name="entry_type"></a>entry_type</summary>

<blockquote>

<details open>
<summary><a name="primitive-testing-entry_type--implementation"></a>implementation: (required)</summary>

<blockquote>

type: `str` <br />
brief: Implementation of a test case. If setup and teardown code is needed, this has to be placed inside the definition. <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-testing-entry_type--implicitly_reliable"></a>implicitly_reliable: (optional)</summary>

<blockquote>

type: `bool` <br />
default: False <br />
brief: Indicates that this primitive is assumed to be 'correct'. This is necessary to break dependency-cycles of different testcases, e.g., most of the primitives need the ability to transfer the result into memory (simd-store). Even a potential test for store would require store to be tested beforehand. To omit such cycles, one can flag a fundamental primitive as implicitly reliable. However, a valid test-implementation must be provided. <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-testing-entry_type--includes"></a>includes: (optional)</summary>

<blockquote>

   same as: [includes](#extension--includes)


</blockquote>
</details>

<details open>
<summary><a name="primitive-testing-entry_type--requires"></a>requires: (optional)</summary>

<blockquote>

type: `list` <br />
entry_type: str <br />
default: [] <br />
brief: A list of required primitives for this test (excluded the current tested primitive). <br />


</blockquote>
</details>

<details open>
<summary><a name="primitive-testing-entry_type--test_name"></a>test_name: (optional)</summary>

<blockquote>

type: `str` <br />
default: default <br />
brief: Name of a specific test definition. <br />


</blockquote>
</details>



</blockquote>
</details>

default: [] <br />
brief: Testing code. <br />
recommended: True <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--tsl_implementation_namespace"></a>tsl_implementation_namespace: (optional)</summary>

<blockquote>

type: `str` <br />
default: functors <br />
brief: Namespace for template specializations. <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

<details>
<summary><a name="primitive--vector_name"></a>vector_name: (optional)</summary>

<blockquote>

type: `str` <br />
default: Vec <br />
brief: The template class name which is referenced from the parameters and within the code. <br />


</blockquote>

[Back to Table of Content](#toc-primitive)

</details>

