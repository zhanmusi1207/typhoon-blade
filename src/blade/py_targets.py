# Copyright (c) 2011 Tencent Inc.
# All rights reserved.
#
# Author: Michaelpeng <michaelpeng@tencent.com>
# Date:   October 20, 2011


"""
 This is python egg target which generates python egg for user.

"""


import os
import blade

import build_rules
import console

from blade_util import var_to_list
from target import Target


class PythonBinaryTarget(Target):
    """A python egg target subclass.

    This class is derived from SconsTarget and generates python egg package.

    """
    def __init__(self,
                 name,
                 srcs,
                 deps,
                 prebuilt,
                 blade,
                 kwargs):
        """Init method. """
        srcs = var_to_list(srcs)
        deps = var_to_list(deps)

        Target.__init__(self,
                        name,
                        'py_binary',
                        srcs,
                        deps,
                        blade,
                        kwargs)

        self.blade = blade
        options = blade.get_options()
        setattr(options, 'generate_dynamic', True)

        if prebuilt:
            self.type = 'prebuilt_py_binary'

    def scons_rules(self):
        """scons_rules.

        Description
        -----------
        It outputs the scons rules according to user options.

        """
        self._clone_env()

        if self.type == 'prebuilt_py_binary':
            return

        env_name = self._env_name()

        setup_file = os.path.join(self.path, 'setup.py')
        python_package = os.path.join(self.path, self.name)
        init_file = os.path.join(python_package, '__init__.py')

        binary_files = []
        if os.path.exists(setup_file):
            binary_files.append(setup_file)

        if not os.path.exists(init_file):
            console.error_exit('The __init__.py not existed in %s' % python_package)
        binary_files.append(init_file)

        dep_var_list = []
        self.targets = self.blade.get_build_targets()
        for dep in self.expanded_deps:
            binary_files += self.targets[dep].data.get('python_sources', [])
            dep_var_list += self.targets[dep].data.get('python_vars', [])

        target_egg_file = '%s.egg' % self._target_file_path()
        python_binary_var = '%s_python_binary_var' % (
            self._generate_variable_name(self.path, self.name))
        self._write_rule('%s = %s.PythonBinary(["%s"], %s)' % (
                          python_binary_var,
                          env_name,
                          target_egg_file,
                          binary_files))
        for var in dep_var_list:
            self._write_rule('%s.Depends(%s, %s)' % (
                             env_name, python_binary_var, var))

        for dynamic_dep_var in self._dynamic_deps_list():
            self._write_rule('%s.Depends(%s, %s)' % (
                             env_name, python_binary_var, dynamic_dep_var))

    def _dep_is_library(self, dep):
        """_dep_is_library.

        Returns
        -----------
        True or False: Whether this dep target is library or not.

        Description
        -----------
        Whether this dep target is library or not.

        """
        build_targets = self.blade.get_build_targets()
        target_type = build_targets[dep].type
        return target_type.endswith('_library')

    def _dynamic_deps_list(self):
        """_dynamic_deps_list.

        Returns
        -----------
        lib_list: the libs list to be dynamically linked into dynamic library

        Description
        -----------
        It will find the libs needed to be linked into the target dynamically.

        """
        build_targets = self.blade.get_build_targets()
        deps = self.expanded_deps
        lib_list = []
        for lib in deps:
            if not self._dep_is_library(lib):
                continue

            if (build_targets[lib].type == 'cc_library' and
                not build_targets[lib].srcs):
                continue
            # system lib
            if lib[0] == '#':
                pass
            else:
                lib_name = self._generate_variable_name(lib[0],
                                                        lib[1],
                                                        'dynamic')

                lib_list.append(lib_name)

        return lib_list

def py_binary(name,
              srcs=[],
              deps=[],
              prebuilt=False,
              **kwargs):
    """python binary - aka, python egg. """
    target = PythonBinaryTarget(name,
                                srcs,
                                deps,
                                prebuilt,
                                blade.blade,
                                kwargs)
    blade.blade.register_target(target)


build_rules.register_function(py_binary)
