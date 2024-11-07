"""
Generate C source with global variables embedding binary/text file contents.
"""

import itertools
import os
from textwrap import dedent


def file2c(source_file, output_directory=None, symbol=None, text=False):
    """
    Generate C source with global variables embedding binary/text file contents

    :param source_file: Source file path.
    :param output_directory: Output directory where source files are generated.
    :param symbol: Global variable symbol name. Defaults to source file name.
    :param text: If true, source file is read as text instead of binary
                 and the generated variable contents are null-terminated.
    """
    if not symbol:
        symbol = os.path.splitext(os.path.basename(source_file))[0]
    if not output_directory:
        output_directory = os.path.dirname(source_file) or os.curdir
    else:
        os.makedirs(output_directory, exist_ok=True)
    
    # Read file contents and format them in a way C will understand
    with open(source_file, "r" if text else "rb") as f:
        contents = f.read()
        if text:
            char_type = "char"
            c_contents = '\n"' + (
                contents
                    .replace("\\", "\\\\")
                    .replace('"', '\\"')
                    .replace("\n", '\\n"\n"')
            ) + '"'
        else:
            char_type = "unsigned char"
            c_contents = "{\n"
            for batch in itertools.batched(contents, n=16):
                c_contents += "  "
                c_contents += ", ".join(hex(b) for b in batch)
                c_contents += ",\n"
            c_contents += "}"

    # Write header file
    header_path = os.path.join(output_directory, symbol + ".h")
    with open(header_path, "w") as header_file:
        header_file.write(dedent("""
            #pragma once

            #include <stdlib.h>

            #ifdef __cplusplus
            extern "C" {{
            #endif

            extern const {char_type} *{symbol};
            extern size_t {symbol}_size;

            #ifdef __cplusplus
            }}
            #endif
        """).format(
            char_type=char_type,
            symbol=symbol,
        ))
    
    # Write implementation file
    implementation_path = os.path.join(output_directory, symbol + ".c")
    with open(implementation_path, "w") as implementation_file:
        implementation_file.write(dedent("""
            #include <stdlib.h>

            static const {char_type} _data[] = {c_contents};

            const {char_type} *{symbol} = _data;
            size_t {symbol}_size = sizeof(_data){minus_one_on_text};
        """).format(
            char_type=char_type,
            symbol=symbol,
            c_contents=c_contents,
            minus_one_on_text=" - 1" if text else "",
        ))


def bin2c(source_file, output_directory=None, symbol=None):
    """
    Alias for file2c that always embed file as binary.
    """
    return file2c(source_file, output_directory, symbol, text=False)


def text2c(source_file, output_directory=None, symbol=None):
    """
    Alias for file2c that always embed file as text.
    """
    return file2c(source_file, output_directory, symbol, text=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        help="Input file",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Output directory",
    )
    parser.add_argument(
        "-s",
        "--symbol",
        help="Global symbol used for the embedded file contents",
    )
    parser.add_argument(
        "-t",
        "--text",
        help="Embed file as text, making sure variable is null-terminated", action="store_true",
    )
    args = parser.parse_args()
    file2c(args.input, args.output_dir, args.symbol, args.text)
