#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bincrafters import build_template_default
import platform
import copy
import os

os.environ['CONAN_USERNAME'] = os.environ.get('CONAN_USERNAME','conanos')

if __name__ == "__main__":

    builder = build_template_default.get_builder()

    if os.environ.get('EMSCRIPTEN_VERSIONS'):
        for version in os.environ['EMSCRIPTEN_VERSIONS'].split(','):
            for build_type in os.environ.get('CONAN_BUILD_TYPES','Debug').split(','):
                builder.add(settings={
                    "compiler": "emcc",
                    "compiler.libcxx":'libcxxabi',
                    "build_type": build_type, 
                    "compiler.version": version
                    },
                    options={'zlib:shared':True}, env_vars={}, build_requires={})

        items = []
        for item in builder.items:
            if not os.environ.get('CONAN_GCC_VERSIONS') and item.settings['compiler'] == 'gcc':
                continue  
            if not os.environ.get('CONAN_CLANG_VERSIONS') and item.settings['compiler'] == 'clang':
                continue 
            items.append(item)

        builder.items = items


    items = []
    for item in builder.items:
        # skip mingw cross-builds
        if not (platform.system() == "Windows" and item.settings["compiler"] == "gcc" and
                item.settings["arch"] == "x86"):
            new_build_requires = copy.copy(item.build_requires)
            # add msys2 and mingw as a build requirement for mingw builds
            if platform.system() == "Windows" and item.settings["compiler"] == "gcc":
                new_build_requires["*"] = new_build_requires.get("*", []) + \
                    ["mingw_installer/1.0@conan/stable",
                     "msys2_installer/latest@bincrafters/stable"]
                items.append([item.settings, item.options, item.env_vars,
                              new_build_requires, item.reference])
            else:
                # or just add build
                items.append(item)
    builder.items = items

    builder.run()
