
find_package(Python3 COMPONENTS Interpreter Development)

set(TSLGenerator ${CMAKE_CURRENT_LIST_DIR}/main.py)
execute_process(
        COMMAND bash -c "LANG=en;lscpu|grep -i flags | tr ' ' '\n' | egrep -v '^Flags:|^$' | sort -d | tr '\n' ' '"
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
    set(Outputs "")
    TSLOutputFilesAsList(Outputs)

    FILE(GLOB tslfiles "${TSLDir}/*")
    if(tslfiles)
        message("YOLO")
        add_custom_command(
                OUTPUT ${Outputs}
                DEPENDS ${CMAKE_CURRENT_LIST_DIR}
                COMMAND python3 ${TSLGenerator} --targets ${TSLHardwareTargets} --no-workaround-warnings --draw-test-dependencies -o ${TSLDir}
        )
    else()
        message("WOLO")
        add_custom_command(
                OUTPUT ${Outputs}
                COMMAND python3 ${TSLGenerator} --targets ${TSLHardwareTargets} --no-workaround-warnings --draw-test-dependencies -o ${TSLDir}
                
        )
    endif()



endfunction()