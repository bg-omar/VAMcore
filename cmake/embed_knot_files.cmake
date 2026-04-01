# CMake script to embed knot resources into C++ source
# Embeds:
#   - all .fseries files recursively from resources/Knots_FourierSeries
#   - all ideal*.txt files recursively from resources/
#   - all .txt files recursively from resources/ideal_12_data (if present)
#
# Generates:
#   - ${CMAKE_BINARY_DIR}/generated/knot_files_embedded.h
#   - ${CMAKE_BINARY_DIR}/generated/knot_files_embedded.cpp
#
# Exposed C++ functions:
#   sst::get_embedded_knot_files()   -> map<knot_id, fseries_text>
#   sst::get_embedded_ideal_files()  -> map<relative_name, text>

set(KNOTS_FOURIER_DIR "${CMAKE_SOURCE_DIR}/resources/Knots_FourierSeries")
set(RESOURCES_DIR     "${CMAKE_SOURCE_DIR}/resources")
set(IDEAL12_DIR       "${RESOURCES_DIR}/ideal_12_data")

set(OUTPUT_FILE "${CMAKE_BINARY_DIR}/generated/knot_files_embedded.cpp")
set(HEADER_FILE "${CMAKE_BINARY_DIR}/generated/knot_files_embedded.h")

file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/generated")

# -------------------------
# Collect resource files
# -------------------------

# Recursive .fseries files under resources/Knots_FourierSeries
set(FSERIES_FILES "")
if(EXISTS "${KNOTS_FOURIER_DIR}")
    file(GLOB_RECURSE FSERIES_FILES RELATIVE "${KNOTS_FOURIER_DIR}" "${KNOTS_FOURIER_DIR}/*.fseries")
endif()

# Recursive ideal*.txt under resources/
set(IDEAL_FILES "")
if(EXISTS "${RESOURCES_DIR}")
    file(GLOB_RECURSE IDEAL_FILES RELATIVE "${RESOURCES_DIR}" "${RESOURCES_DIR}/ideal*.txt")
endif()

# Also include all txt files under resources/ideal_12_data (even if names differ)
set(IDEAL12_TXT_FILES "")
if(EXISTS "${IDEAL12_DIR}")
    file(GLOB_RECURSE IDEAL12_TXT_FILES RELATIVE "${RESOURCES_DIR}" "${IDEAL12_DIR}/*.txt")
endif()

# Merge and de-duplicate ideal text lists
set(ALL_IDEAL_TEXT_FILES ${IDEAL_FILES} ${IDEAL12_TXT_FILES})
list(REMOVE_DUPLICATES ALL_IDEAL_TEXT_FILES)

# -------------------------
# Helpers
# -------------------------

# Pick a raw string delimiter unlikely to collide with file content
function(_sst_pick_delim out_var content)
    set(_delim "SST_EMBED_DELIM")
    string(FIND "${content}" ")${_delim}\"" _pos)
    if(NOT _pos EQUAL -1)
        foreach(i RANGE 1 200)
            set(_cand "SST_EMBED_DELIM_${i}")
            string(FIND "${content}" ")${_cand}\"" _pos2)
            if(_pos2 EQUAL -1)
                set(_delim "${_cand}")
                break()
            endif()
        endforeach()
    endif()
    set(${out_var} "${_delim}" PARENT_SCOPE)
endfunction()

# Escape only for C++ string key literals (not file content)
function(_sst_escape_cpp_string out_var in_str)
    set(_s "${in_str}")
    string(REPLACE "\\" "\\\\" _s "${_s}")
    string(REPLACE "\"" "\\\"" _s "${_s}")
    set(${out_var} "${_s}" PARENT_SCOPE)
endfunction()

# Append a potentially huge text blob as concatenated raw string literals (MSVC-safe)
# MSVC C2026: keep each literal well under 16k (use 8k to be safe across versions)
function(_sst_append_chunked_raw_string out_file lhs_key file_content)
    set(_chunk_size 8192)
    string(LENGTH "${file_content}" _len)
    file(APPEND "${out_file}" "    ${lhs_key} =\n")
    set(_offset 0)
    while(_offset LESS _len)
        math(EXPR _remaining "${_len} - ${_offset}")
        if(_remaining GREATER _chunk_size)
            set(_take ${_chunk_size})
        else()
            set(_take ${_remaining})
        endif()
        string(SUBSTRING "${file_content}" ${_offset} ${_take} _chunk)
        _sst_pick_delim(_delim "${_chunk}")
        file(APPEND "${out_file}" "        R\"${_delim}(${_chunk})${_delim}\"\n")
        math(EXPR _offset "${_offset} + ${_take}")
    endwhile()
    file(APPEND "${out_file}" "    ;\n")
endfunction()

# -------------------------
# Generate header
# -------------------------
file(WRITE "${HEADER_FILE}" "// Auto-generated header - do not edit manually\n")
file(APPEND "${HEADER_FILE}" "#ifndef KNOT_FILES_EMBEDDED_H\n")
file(APPEND "${HEADER_FILE}" "#define KNOT_FILES_EMBEDDED_H\n\n")
file(APPEND "${HEADER_FILE}" "#include <map>\n")
file(APPEND "${HEADER_FILE}" "#include <string>\n\n")
file(APPEND "${HEADER_FILE}" "namespace sst {\n")
file(APPEND "${HEADER_FILE}" "    std::map<std::string, std::string> get_embedded_knot_files();\n")
file(APPEND "${HEADER_FILE}" "    std::map<std::string, std::string> get_embedded_ideal_files();\n")
file(APPEND "${HEADER_FILE}" "}\n\n")
file(APPEND "${HEADER_FILE}" "#endif // KNOT_FILES_EMBEDDED_H\n")

# -------------------------
# Generate source
# -------------------------
file(WRITE "${OUTPUT_FILE}" "// Auto-generated file - do not edit manually\n")
file(APPEND "${OUTPUT_FILE}" "// Embedded knot .fseries and ideal database / coordinate text resources\n\n")
file(APPEND "${OUTPUT_FILE}" "#include \"knot_files_embedded.h\"\n")
file(APPEND "${OUTPUT_FILE}" "#include <map>\n")
file(APPEND "${OUTPUT_FILE}" "#include <string>\n\n")
file(APPEND "${OUTPUT_FILE}" "namespace sst {\n\n")

# ---- get_embedded_knot_files() ----
file(APPEND "${OUTPUT_FILE}" "std::map<std::string, std::string> get_embedded_knot_files() {\n")
file(APPEND "${OUTPUT_FILE}" "    std::map<std::string, std::string> files;\n\n")

set(FSERIES_COUNT 0)
foreach(rel_fseries IN LISTS FSERIES_FILES)
    set(abs_fseries "${KNOTS_FOURIER_DIR}/${rel_fseries}")
    get_filename_component(filename "${abs_fseries}" NAME)

    # Prefer knot.<id>.fseries naming if present
    string(REGEX REPLACE "^knot\\.(.+)\\.fseries$" "\\1" knot_id "${filename}")
    if("${knot_id}" STREQUAL "${filename}")
        # Fallback: use relative path stem, normalized to forward slashes
        get_filename_component(stem "${rel_fseries}" NAME_WE)
        get_filename_component(rel_dir "${rel_fseries}" DIRECTORY)
        if(rel_dir AND NOT rel_dir STREQUAL "")
            set(knot_id "${rel_dir}/${stem}")
        else()
            set(knot_id "${stem}")
        endif()
        string(REPLACE "\\" "/" knot_id "${knot_id}")
    endif()

    file(READ "${abs_fseries}" file_content)
    _sst_escape_cpp_string(_knot_id_escaped "${knot_id}")
    _sst_append_chunked_raw_string("${OUTPUT_FILE}" "files[\"${_knot_id_escaped}\"]" "${file_content}")
    math(EXPR FSERIES_COUNT "${FSERIES_COUNT} + 1")
endforeach()

file(APPEND "${OUTPUT_FILE}" "\n    return files;\n")
file(APPEND "${OUTPUT_FILE}" "}\n\n")

# ---- get_embedded_ideal_files() ----
file(APPEND "${OUTPUT_FILE}" "std::map<std::string, std::string> get_embedded_ideal_files() {\n")
file(APPEND "${OUTPUT_FILE}" "    std::map<std::string, std::string> files;\n\n")

set(IDEAL_COUNT 0)
foreach(rel_txt IN LISTS ALL_IDEAL_TEXT_FILES)
    set(abs_txt "${RESOURCES_DIR}/${rel_txt}")
    if(NOT EXISTS "${abs_txt}")
        continue()
    endif()

    # key = relative path under resources (portable + unique)
    string(REPLACE "\\" "/" ideal_key "${rel_txt}")

    file(READ "${abs_txt}" txt_content)
    _sst_escape_cpp_string(_ideal_key_escaped "${ideal_key}")
    _sst_append_chunked_raw_string("${OUTPUT_FILE}" "files[\"${_ideal_key_escaped}\"]" "${txt_content}")
    math(EXPR IDEAL_COUNT "${IDEAL_COUNT} + 1")
endforeach()

file(APPEND "${OUTPUT_FILE}" "\n    return files;\n")
file(APPEND "${OUTPUT_FILE}" "}\n\n")

file(APPEND "${OUTPUT_FILE}" "} // namespace sst\n")

message(STATUS "Embedded ${FSERIES_COUNT} .fseries files from ${KNOTS_FOURIER_DIR}")
message(STATUS "Embedded ${IDEAL_COUNT} ideal text files from ${RESOURCES_DIR}")