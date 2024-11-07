#!/usr/bin/env python
"""
Generate C source with global variables embedding binary/text file contents.
"""

import itertools
import os
import sys
from textwrap import dedent


def file2c(
    source_file: str,
    output: str | None = None,
    symbol: str | None = None,
    header=False,
    text=False,
):
    """
    Generate C source with global variables embedding binary/text file contents

    :param source_file: Source file path.
    :param output_directory: Output directory where source files are generated.
    :param symbol: Global variable symbol name. Defaults to source file name.
    :param header: Generate header content instead of implementation.
    :param text: If true, source file is read as text instead of binary
                 and the generated variable contents are null-terminated.
    """
    if not symbol:
        symbol = os.path.splitext(os.path.basename(source_file))[0]
    if output and (dirname := os.path.dirname(output)):
        os.makedirs(dirname, exist_ok=True)

    # Write header file
    if header:
        with (open(output, "w") if output else sys.stdout) as f:
            f.write(dedent("""
                #pragma once

                #include <stdlib.h>

                #ifdef __cplusplus
                extern "C" {{
                #endif

                extern const {char_type} *{name};
                extern const size_t {name}_size;

                #ifdef __cplusplus
                }}
                #endif
            """).format(
                char_type="char" if text else "unsigned char",
                name=symbol,
            ).lstrip())
    # Write implementation file
    else:
        # Read file contents and format them in a way C will understand
        with open(source_file, "r" if text else "rb") as f:
            contents = f.read()
            if text:
                c_contents = '\n"' + (
                    contents
                        .replace("\\", "\\\\")
                        .replace('"', '\\"')
                        .replace("\n", '\\n"\n"')
                ) + '"'
            else:
                c_contents = "{\n"
                for batch in itertools.batched(contents, n=16):
                    c_contents += "  "
                    c_contents += ", ".join(hex(b) for b in batch)
                    c_contents += ",\n"
                c_contents += "}"

        with (open(output, "w") if output else sys.stdout) as f:
            f.write(dedent("""
                #include <stdlib.h>

                static const {char_type} _data[] = {c_contents};

                const {char_type} *{name} = _data;
                const size_t {name}_size = sizeof(_data){minus_one_on_text};
            """).format(
                char_type="char" if text else "unsigned char",
                name=symbol,
                c_contents=c_contents,
                minus_one_on_text=" - 1" if text else "",
            ).lstrip())


def bin2c(source_file, output_directory=None, symbol=None, header=False):
    """
    Alias for file2c that always embed file as binary.
    """
    return file2c(source_file, output_directory, symbol, header, text=False)


def text2c(source_file, output_directory=None, symbol=None, header=False):
    """
    Alias for file2c that always embed file as text.
    """
    return file2c(source_file, output_directory, symbol, header, text=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        help="Input file",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file",
    )
    parser.add_argument(
        "-s",
        "--symbol",
        help="Global symbol used for the embedded file contents",
    )
    parser.add_argument(
        "--header",
        help="Generate a header with the definitions instead of the implementation file",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--text",
        help="Embed file as text, making sure variable is null-terminated",
        action="store_true",
    )
    args = parser.parse_args()
    file2c(args.input, args.output, args.symbol, args.header, args.text)
