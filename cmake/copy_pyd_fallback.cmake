# copy_pyd_fallback.cmake
# Run at build time: copy SOURCE to PROJECT_ROOT, examples/, tests/, SwirlStringTheory/, SwirlStringTheory/papers/SST-31_Canon/, SST_Dashboard/.
# SOURCE is typically sstcore.*.pyd or sstbindings.*.pyd.
# Never fails the build; warns if a copy fails (e.g. file locked by Python).
# Invoke: cmake -P copy_pyd_fallback.cmake -DSOURCE=<path> -DPROJECT_ROOT=<path> [-DBUILD_DIR=<path>]
# If SOURCE is empty, tries BUILD_DIR/Release/*.pyd and BUILD_DIR/*.pyd (for multi-config generators).

set(SOURCE_FILE "")

if(SOURCE AND EXISTS "${SOURCE}")
  set(SOURCE_FILE "${SOURCE}")
endif()

if(NOT SOURCE_FILE AND BUILD_DIR)
  foreach(SUBDIR "Release" "Debug" "")
    if(SUBDIR STREQUAL "")
      set(SEARCH "${BUILD_DIR}")
    else()
      set(SEARCH "${BUILD_DIR}/${SUBDIR}")
    endif()
    if(EXISTS "${SEARCH}")
      file(GLOB PYD_LIST "${SEARCH}/*.pyd")
      list(LENGTH PYD_LIST N)
      if(N GREATER 0)
        list(GET PYD_LIST 0 SOURCE_FILE)
        break()
      endif()
    endif()
  endforeach()
endif()

if(NOT SOURCE_FILE OR NOT EXISTS "${SOURCE_FILE}")
  message(WARNING "copy_pyd_fallback: SOURCE missing or not found (SOURCE=${SOURCE}, BUILD_DIR=${BUILD_DIR})")
  return()
endif()
if(NOT PROJECT_ROOT)
  message(WARNING "copy_pyd_fallback: PROJECT_ROOT not set")
  return()
endif()

get_filename_component(FILENAME "${SOURCE_FILE}" NAME)

set(DESTS
  "${PROJECT_ROOT}/${FILENAME}"
  "${PROJECT_ROOT}/examples/${FILENAME}"
  "${PROJECT_ROOT}/tests/${FILENAME}"
  "${PROJECT_ROOT}/../SwirlStringTheory/${FILENAME}"
  "${PROJECT_ROOT}/../SwirlStringTheory/papers/SST-31_Canon/${FILENAME}"
  "${PROJECT_ROOT}/../SST_Dashboard/${FILENAME}"
)

set(COPIED 0)
foreach(DEST IN LISTS DESTS)
  get_filename_component(DEST_DIR "${DEST}" DIRECTORY)
  if(DEST_DIR)
    execute_process(COMMAND "${CMAKE_COMMAND}" -E make_directory "${DEST_DIR}" RESULT_VARIABLE _mk)
  endif()
  execute_process(
    COMMAND "${CMAKE_COMMAND}" -E copy "${SOURCE_FILE}" "${DEST}"
    RESULT_VARIABLE RV
    ERROR_QUIET
    OUTPUT_QUIET
  )
  if(RV EQUAL 0)
    math(EXPR COPIED "${COPIED} + 1")
  else()
    message(WARNING "Could not copy to ${DEST} (file may be in use). Copy manually if needed.")
  endif()
endforeach()

if(COPIED GREATER 0)
  message(STATUS "Copied sstcore module to ${COPIED} location(s) for easy import")
endif()
