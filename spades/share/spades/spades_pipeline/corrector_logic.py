#!/usr/bin/python3 -O

############################################################################
# Copyright (c) 2015 Saint Petersburg State University
# Copyright (c) 2011-2014 Saint Petersburg Academic University
# All Rights Reserved
# See file LICENSE for details.
############################################################################


import os
import sys
import shutil
import support
import process_cfg
from site import addsitedir



def prepare_config_corr(filename, cfg, ext_python_modules_home):
    addsitedir(ext_python_modules_home)
    if sys.version.startswith('2.'):
        import yaml as pyyaml
    elif sys.version.startswith('3.'):
        import yaml as pyyaml
    data = pyyaml.load(open(filename, 'r'), Loader=pyyaml.FullLoader)
    data["dataset"] = cfg.dataset
    data["output_dir"] = cfg.output_dir
    data["work_dir"] = cfg.tmp_dir
    #data["hard_memory_limit"] = cfg.max_memory
    data["max_nthreads"] = cfg.max_threads
    data["bwa"] = cfg.bwa
    file_c = open(filename, 'w')
    pyyaml.dump(data, file_c,
                default_flow_style=False, default_style='"', width=float("inf"))
    file_c.close()


# shutil.copyfile does not copy any metadata (time and permission), so one
# cannot expect preserve_mode = False and preserve_times = True to work.
def copy_tree(src, dst, preserve_times = True, preserve_mode = True):
    if preserve_mode == False:
        copy_fn = shutil.copyfile
    else:
        copy_fn = shutil.copy2

    # shutil.copytree preserves the timestamp, so we must update it afterwards.
    shutil.copytree(src, dst, copy_function = copy_fn, dirs_exist_ok = True)

    if preserve_times == False:
        for dirpath, _, filenames in os.walk(dst):
            os.utime(dirpath, None)
            for file in filenames:
                os.utime(os.path.join(dirpath, file), None)


def run_corrector(configs_dir, execution_home, cfg,
                ext_python_modules_home, log, to_correct, result):
    addsitedir(ext_python_modules_home)
    if sys.version.startswith('2.'):
        import yaml as pyyaml
    elif sys.version.startswith('3.'):
        import yaml as pyyaml

    dst_configs = os.path.join(cfg.output_dir, "configs")
    if os.path.exists(dst_configs):
        shutil.rmtree(dst_configs)
    copy_tree(os.path.join(configs_dir, "corrector"), dst_configs, preserve_times=False)
    cfg_file_name = os.path.join(dst_configs, "corrector.info")

    cfg.tmp_dir = support.get_tmp_dir(prefix="corrector_")

    prepare_config_corr(cfg_file_name, cfg, ext_python_modules_home)
    binary_name = "spades-corrector-core"

    command = [os.path.join(execution_home, binary_name),
               os.path.abspath(cfg_file_name), os.path.abspath(to_correct)]

    log.info("\n== Running contig polishing tool: " + ' '.join(command) + "\n")


    log.info("\n== Dataset description file was created: " + cfg_file_name + "\n")

    support.sys_call(command, log)
    if not os.path.isfile(result):
        support.error("Mismatch correction finished abnormally: " + result + " not found!")
    if os.path.isdir(cfg.tmp_dir):
        shutil.rmtree(cfg.tmp_dir)





