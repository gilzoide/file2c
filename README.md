# file2c
Python script that generates C source files with global variables embedding binary/text file contents, with easy integration for CMake projects.


## Features
- Single executable Python script, easy to install/copy or use as Git submodule
- Works as both a CLI script and as a Python module
- Supports embedding files as binary or text
  + Binary file contents have `const unsigned char *` type
  + Text file contents have `const char *` type and are guaranteed to be null-terminated
- File content size is available as an additional global variable
- Generated header is compatible with both C and C++
- [file2c.cmake](file2c.cmake) script for easy integration with CMake projects


## Usage
```
python file2c.py INPUT [-o OUTPUT] [-s SYMBOL] [--text] [--header]
```


## Examples
```sh
# Generate `file.c` and `file.h` from binary contents of `file.txt`:
#   `const unsigned char *file`: file contents as a byte string
#   `const size_t file_size`: file size
python file2c.py file.txt -o file.c
python file2c.py file.txt -o file.h --header

# Generate `file.c` and `file.h` from text contents of `file.txt`:
#   `const char *file`: file contents as a null-terminated char string
#   `const size_t file_size`: file size
python file2c.py file.txt --text -o file.c
python file2c.py file.txt --text -o file.h --header

# Generate `file.c` and `file.h` from binary contents of `file.txt`,
# customizing the variable symbol name to "contents":
#   `const unsigned char *contents`: file contents as a byte string
#   `const size_t contents_size`: file size
python file2c.py file.txt --symbol contents -o file.c
python file2c.py file.txt --symbol contents -o file.h --header
```


## Integrating with CMake
In CMake:
```cmake
# 1. Include file2c.cmake script
include(path/to/file2c.cmake)

# 2. Generate C library
add_file2c(
  new_library_target
  INPUT input_file_to_be_embedded
  # Optional: choose the name of the global variable/header file
  # Defaults to input file name
  SYMBOL some_c_symbol
  # Pass "TEXT" to embed contents as text, omit for binary contents
  TEXT
)

# 3. Link the generated library with other targets
target_link_libraries(my_existing_target new_library_target)
```

In C/C++:
```c
// 1. Include generated header
#include <some_c_symbol.h>

// 2. Use the embedded contents
void print_contents() {
  printf("Content: %s\n", some_c_symbol);
  printf("Size: %lu\n", some_c_symbol_size);
}
```
