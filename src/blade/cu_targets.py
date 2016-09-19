# Copyright (c) 2013 Tencent Inc.
# All rights reserved.
#
# Author: LI Yi <sincereli@tencent.com>
# Created:   September 27, 2013


"""
 This is the cu_target module which is the super class
 of all of the scons cu targets, like cu_library, cu_binary.

"""

import os
import blade

import build_rules
from blade_util import var_to_list
from cc_targets import CcTarget


class CuTarget(CcTarget):
    """A scons cu target subclass.

    This class is derived from SconsCcTarget and it is the base class
    of cu_library, cu_binary etc.

    """
    def __init__(self,
                 name,
                 target_type,
                 srcs,
                 deps,
                 warning,
                 defs,
                 incs,
                 extra_cppflags,
                 extra_linkflags,
                 blade,
                 kwargs):
        """Init method.

        Init the cu target.

        """
        srcs = var_to_list(srcs)
        deps = var_to_list(deps)
        extra_cppflags = var_to_list(extra_cppflags)
        extra_linkflags = var_to_list(extra_linkflags)

        CcTarget.__init__(self,
                          name,
                          target_type,
                          srcs,
                          deps,
                          warning,
                          defs,
                          incs,
                          [], [],
                          extra_cppflags,
                          extra_linkflags,
                          blade,
                          kwargs)

#    def _get_cu_flags(self):
#        """_get_cu_flags.
#
#        Return the nvcc flags according to the BUILD file and other configs.
#
#        """
#        nvcc_flags = []
#
#        # Warnings
#        if self.data.get('warning', '') == 'no':
#            nvcc_flags.append('-w')
#
#        # Defs
#        defs = self.data.get('defs', [])
#        nvcc_flags += [('-D' + macro) for macro in defs]
#
#        # Optimize flags
#
#        if (self.blade.get_options().profile == 'release' or
#            self.data.get('always_optimize')):
#            nvcc_flags += self._get_optimize_flags()
#
#        # Incs
#        incs = self.data.get('incs', [])
#        new_incs_list = [os.path.join(self.path, inc) for inc in incs]
#        new_incs_list += self._export_incs_list()
#        # Remove duplicate items in incs list and keep the order
#        incs_list = []
#        for inc in new_incs_list:
#            new_inc = os.path.normpath(inc)
#            if new_inc not in incs_list:
#                incs_list.append(new_inc)
#
#        return (nvcc_flags, incs_list)


    def _get_cu_flags(self):
        """_get_cu_flags.

        Return the nvcc flags according to the BUILD file and other configs.

        """
        nvcc_flags = []

        # Warnings
        if self.data.get('warning', '') == 'no':
            nvcc_flags.append('-w')

        # Defs
        defs = self.data.get('defs', [])
        nvcc_flags += [('-D' + macro) for macro in defs]

        # Optimize flags

        if (self.blade.get_options().profile == 'release' or
            self.data.get('always_optimize')):
            nvcc_flags += self._get_optimize_flags()
        #added by jamesyue
        nvcc_flags += self.data.get('extra_cppflags', [])

        # Incs
        incs = self.data.get('incs', [])
        new_incs_list = [os.path.join(self.path, inc) for inc in incs]
        new_incs_list += self._export_incs_list()
        # Remove duplicate items in incs list and keep the order
        incs_list = []
        for inc in new_incs_list:
            new_inc = os.path.normpath(inc)
            if new_inc not in incs_list:
                incs_list.append(new_inc)
        cc_flags_from_option, cc_incs_list = self._get_cc_flags() 
        
        return (nvcc_flags, incs_list)


    def _cu_objects_rules(self):
        """_cu_library rules. """
        env_name = self._env_name()
        var_name = self._generate_variable_name(self.path, self.name)
        flags_from_option, incs_list = self._get_cu_flags()
        incs_string = " -I".join(incs_list)
        flags_string = " ".join(flags_from_option)
        objs = []
        sources = []
        targets = []
        for src in self.srcs:
            obj = '%s_%s_object' % (self._generate_variable_name(var_name, src), #modified by jamesyue to avoid the link error
                                    self._regular_variable_name(self.name))
            target_path = os.path.join(
                    self.build_path, self.path, '%s.objs' % self.name, src)
            self._write_rule(
                    '%s = %s.NvccObject(NVCCFLAGS="-I%s %s", target="%s" + top_env["OBJSUFFIX"]'
                    ', source="%s")' % (obj,
                                        env_name,
                                        incs_string,
                                        flags_string,
                                        target_path,
                                        self._target_file_path(self.path, src)))
            self._write_rule('%s.Depends(%s, "%s")' % (
                             env_name,
                             obj,
                             self._target_file_path(self.path, src)))
            sources.append(self._target_file_path(self.path, src))
            targets.append(target_path)
            objs.append(obj)
        '''
        for src in self.srcs:
            obj = '%s_%s_object' % (var_name,
                                    self._regular_variable_name(self.name))
            obj_nvcc = obj + "_nvccobj"
            target_path = os.path.join(
                    self.build_path, self.path, '%s.objs' % self.name, src)
            self._write_rule(
                    '%s = %s.NvccObject(NVCCFLAGS="-I%s %s", target="%s" + top_env["OBJSUFFIX"]'
                    ', source="%s")' % (obj_nvcc,
                                        env_name,
                                        incs_string,
                                        flags_string,
                                        target_path,
                                        self._target_file_path(self.path, src)))

            self._write_rule(
                    '%s = %s.SharedObject(source = %s)' % (obj,
                                          env_name,
                                          obj_nvcc))

            self._write_rule('%s.Depends(%s, "%s")' % (
                             env_name,
                             obj_nvcc,
                             self._target_file_path(self.path, src)))

            self._write_rule('%s.Depends(%s, %s)' % (
                             env_name,
                             obj,
                             obj_nvcc))
            sources.append(self._target_file_path(self.path, src))
            objs.append(obj)
        '''
        self._write_rule('%s = [%s]' % (self._objs_name(), ','.join(objs)))
        return sources,targets


class CuLibrary(CuTarget):
    """A scons cu target subclass

    This class is derived from SconsCuTarget and it generates the cu_library
    rules according to user options.
    """
    def __init__(self,
                 name,
                 srcs,
                 deps,
                 warning,
                 defs,
                 incs,
                 extra_cppflags,
                 extra_linkflags,
                 link_all_symbols,
                 blade,
                 kwargs):
        type = 'cu_library'
        CuTarget.__init__(self,
                          name,
                          type,
                          srcs,
                          deps,
                          warning,
                          defs,
                          incs,
                          extra_cppflags,
                          extra_linkflags,
                          blade,
                          kwargs)
        self.data['link_all_symbols'] = link_all_symbols

    def scons_rules(self):
        """scons_rules.

        It outputs the scons rules according to user options.
        """
        self._prepare_to_generate_rule()
        sources,targets = self._cu_objects_rules()

        options = self.blade.get_options()
        build_dynamic = (getattr(options, 'generate_dynamic', False) or
                         self.data.get('build_dynamic'))
        if build_dynamic:
            targets = map(lambda x: '"'+x+'"', map(lambda x: x+".o", targets))
            self._dynamic_cu_library(targets)
        else:
            pass
        self._cc_library()


    def _dynamic_cu_library(self, targets):
        """_dynamic_cu_library.

        It will output the dynamic_cu_library rule into the buffer.

        """
        self._setup_link_flags()

        var_name = self._generate_variable_name(self.path,
                                                self.name,
                                                'dynamic')

        lib_str = self._get_dynamic_deps_lib_list()
        if self.srcs or self.expanded_deps:
            self._write_rule('%s.Append(LINKFLAGS=["-Xlinker", "--no-undefined"])'
                             % self._env_name())
            #rule = '%s = %s.SharedLibrary("%s", source=[%s], %s)' % (
            rule = '%s = %s.StaticLibrary("%s", source=[%s], %s)' % (
                    var_name,
                    self._env_name(),
                    self._target_file_path(),
                    ','.join(targets),
                    lib_str)
            self._write_rule(rule)

def cu_library(name,
               srcs=[],
               deps=[],
               warning='yes',
               defs=[],
               incs=[],
               extra_cppflags=[],
               extra_linkflags=[],
               link_all_symbols=False,
               **kwargs):
    target = CuLibrary(name,
                       srcs,
                       deps,
                       warning,
                       defs,
                       incs,
                       extra_cppflags,
                       extra_linkflags,
                       link_all_symbols,
                       blade.blade,
                       kwargs)
    blade.blade.register_target(target)


build_rules.register_function(cu_library)


class CuBinary(CuTarget):
    """A scons cu target subclass

    This class is derived from SconsCuTarget and it generates the cu_binary
    rules according to user options.
    """
    def __init__(self,
                 name,
                 srcs,
                 deps,
                 warning,
                 defs,
                 incs,
                 extra_cppflags,
                 extra_linkflags,
                 blade,
                 kwargs):
        type = 'cu_binary'
        CuTarget.__init__(self,
                          name,
                          type,
                          srcs,
                          deps,
                          warning,
                          defs,
                          incs,
                          extra_cppflags,
                          extra_linkflags,
                          blade,
                          kwargs)

    def _cc_binary(self):
        """_cc_binary rules. """
        env_name = self._env_name()
        var_name = self._generate_variable_name(self.path, self.name)

        platform = self.blade.get_scons_platform()

        (link_all_symbols_lib_list,
         lib_str,
         whole_link_flags) = self._get_static_deps_lib_list()
        if whole_link_flags:
            self._write_rule(
                    '%s.Append(LINKFLAGS=[%s])' % (env_name, whole_link_flags))

        if self.data.get('export_dynamic'):
            self._write_rule(
                '%s.Append(LINKFLAGS="-rdynamic")' % env_name)

        self._setup_link_flags()

        self._write_rule('{0}.Replace('
                       'CC={0}["NVCC"], '
                       'CPP={0}["NVCC"], '
                       'CXX={0}["NVCC"], '
                       'LINK={0}["NVCC"])'.format(env_name))

        self._write_rule('%s = %s.Program("%s", %s, %s)' % (
            var_name,
            env_name,
            self._target_file_path(),
            self._objs_name(),
            lib_str))
        self._write_rule('%s.Depends(%s, %s)' % (
            env_name,
            var_name,
            self._objs_name()))

        if link_all_symbols_lib_list:
            self._write_rule('%s.Depends(%s, [%s])' % (
                    env_name, var_name, ', '.join(link_all_symbols_lib_list)))

        #self._write_rule('%s.Append(LINKFLAGS=str(version_obj[0]))' % env_name)
        self._write_rule('%s.Requires(%s, version_obj)' % (
                         env_name, var_name))

    def scons_rules(self):
        """scons_rules.

        It outputs the scons rules according to user options.
        """
        self._prepare_to_generate_rule()
        self._cu_objects_rules()
        self._cc_binary()


def cu_binary(name,
              srcs=[],
              deps=[],
              warning='yes',
              defs=[],
              incs=[],
              extra_cppflags=[],
              extra_linkflags=[],
              **kwargs):
    target = CuBinary(name,
                      srcs,
                      deps,
                      warning,
                      defs,
                      incs,
                      extra_cppflags,
                      extra_linkflags,
                      blade.blade,
                      kwargs)
    blade.blade.register_target(target)


build_rules.register_function(cu_binary)
