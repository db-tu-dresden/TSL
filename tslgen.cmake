
find_package(Python3 COMPONENTS Interpreter Development)

set(TSLGenerator ${CMAKE_CURRENT_LIST_DIR}/main.py)
set(TSLGeneratorFilesNeedsGenerationCommand ${CMAKE_CURRENT_LIST_DIR}/needs_rebuild.py)
set(TSLAfterGenerationCommand ${CMAKE_CURRENT_LIST_DIR}/rebuild_fileslist.py)

execute_process(
        COMMAND bash -c "LANG=en;lscpu|grep -i flags | tr ' ' '\n' | egrep -v '^Flags:|^$' | sort -d | tr '\n' ';'"
        OUTPUT_VARIABLE TSLHardwareTargets
        RESULT_VARIABLE TSLHardwareReturnValue
)
if(NOT TSLHardwareReturnValue EQUAL 0)
    message(FATAL_ERROR "Could not determine hardware flags. Please specify them manually.")
endif()


function(TSLOutputFilesAsList Outputs)
    execute_process(
            COMMAND python3 ${TSLGenerator} --targets ${TSLHardwareTargets} --print-outputs-only
            OUTPUT_VARIABLE FilesList
            RESULT_VARIABLE ReturnValue
    )
    if(NOT ReturnValue EQUAL 0)
        message(FATAL_ERROR "Failed to get the files-to-be-generated from tsl.")
    endif()
    set(${Outputs} ${FilesList} PARENT_SCOPE)
endfunction()

function(TSLGenerate TSLDir)
    message("TSL Lib will be in: ${TSLDir}")
    message("Detected Hardware:  ${TSLHardwareTargets}")
    execute_process(
            COMMAND python3 ${TSLGeneratorFilesNeedsGenerationCommand}
            COMMAND_ECHO STDOUT
            RESULT_VARIABLE NeedsGeneration
    )
    if(NeedsGeneration EQUAL 0)
        execute_process(
                COMMAND python3 ${TSLGenerator} --targets ${TSLHardwareTargets} --no-workaround-warnings --draw-test-dependencies -o ${TSLDir}
                COMMAND_ECHO STDOUT
        )
        execute_process(
                COMMAND python3 ${TSLAfterGenerationCommand}
                COMMAND_ECHO STDOUT
        )
    endif()
endfunction()
