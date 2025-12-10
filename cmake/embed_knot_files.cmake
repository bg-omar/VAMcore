# CMake script to embed .fseries files into C++ source
# This generates a C++ file with embedded knot data

set(KNOT_FSERIES_DIR "${CMAKE_SOURCE_DIR}/src/knot_fseries")
set(OUTPUT_FILE "${CMAKE_BINARY_DIR}/generated/knot_files_embedded.cpp")
set(HEADER_FILE "${CMAKE_BINARY_DIR}/generated/knot_files_embedded.h")

# Create output directory
file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/generated")

# Find all .fseries files
file(GLOB FSERIES_FILES "${KNOT_FSERIES_DIR}/*.fseries")

# Start generating the header file first
file(WRITE "${HEADER_FILE}" "// Auto-generated header - do not edit manually\n")
file(APPEND "${HEADER_FILE}" "#ifndef KNOT_FILES_EMBEDDED_H\n")
file(APPEND "${HEADER_FILE}" "#define KNOT_FILES_EMBEDDED_H\n\n")
file(APPEND "${HEADER_FILE}" "#include <map>\n")
file(APPEND "${HEADER_FILE}" "#include <string>\n\n")
file(APPEND "${HEADER_FILE}" "namespace sst {\n")
file(APPEND "${HEADER_FILE}" "    std::map<std::string, std::string> get_embedded_knot_files();\n")
file(APPEND "${HEADER_FILE}" "}\n\n")
file(APPEND "${HEADER_FILE}" "#endif // KNOT_FILES_EMBEDDED_H\n")

# Start generating the C++ source file
file(WRITE "${OUTPUT_FILE}" "// Auto-generated file - do not edit manually\n")
file(APPEND "${OUTPUT_FILE}" "// This file contains embedded .fseries knot data\n\n")
file(APPEND "${OUTPUT_FILE}" "#include \"knot_files_embedded.h\"\n")
file(APPEND "${OUTPUT_FILE}" "#include <map>\n")
file(APPEND "${OUTPUT_FILE}" "#include <string>\n\n")
file(APPEND "${OUTPUT_FILE}" "namespace sst {\n\n")
file(APPEND "${OUTPUT_FILE}" "std::map<std::string, std::string> get_embedded_knot_files() {\n")
file(APPEND "${OUTPUT_FILE}" "    std::map<std::string, std::string> files;\n\n")

# Process each .fseries file
set(FSERIES_COUNT 0)
foreach(fseries_file ${FSERIES_FILES})
    get_filename_component(filename "${fseries_file}" NAME)
    # Extract knot ID (e.g., "3_1" from "knot.3_1.fseries")
    string(REGEX REPLACE "^knot\\.(.+)\\..*$" "\\1" knot_id "${filename}")
    
    # Read file content
    file(READ "${fseries_file}" file_content)
    
    # Use raw string literal with custom delimiter
    set(DELIM "KNOT_FILE_DELIM")
    
    # Add to the map using raw string literal with custom delimiter
    file(APPEND "${OUTPUT_FILE}" "    files[\"${knot_id}\"] = R\"${DELIM}(${file_content})${DELIM}\";\n")
    math(EXPR FSERIES_COUNT "${FSERIES_COUNT} + 1")
endforeach()

file(APPEND "${OUTPUT_FILE}" "\n    return files;\n")
file(APPEND "${OUTPUT_FILE}" "}\n\n")
file(APPEND "${OUTPUT_FILE}" "} // namespace sst\n")

message(STATUS "Embedded ${FSERIES_COUNT} .fseries files into C++ source")
