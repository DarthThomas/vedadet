import shutil
import argparse
import copy
import os
import os.path as osp
import time
import warnings

import torch

from vedacore.misc import mkdir_or_exist, Config
from vedadet.misc import get_root_logger
from vedacore.misc import set_random_seed
from vedadet.assembler import trainval


def parse_args():
    parser = argparse.ArgumentParser(description='Train a detector')
    parser.add_argument('config', help='train config file path')
    parser.add_argument('--workdir', help='the dir to save logs and models')
    parser.add_argument('--launcher',
                        choices=['none', 'pytorch'],
                        default='none',
                        help='job launcher')
    parser.add_argument('--local_rank', type=int, default=0)  # TODO

    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    cfg = Config.fromfile(args.config)

    # workdir is determined in this priority: CLI > segment in file > filename
    if args.workdir is not None:
        # update configs according to CLI args if args.work_dir is not None
        cfg.workdir = args.workdir
    elif cfg.get('workdir', None) is None:
        # use config filename as default work_dir if cfg.work_dir is None
        cfg.workdir = osp.join('./workdir',
                               osp.splitext(osp.basename(args.config))[0])

    seed = cfg.get('seed', None)
    deterministic = cfg.get('deterministic', False)
    set_random_seed(seed, deterministic)

    # create work_dir
    mkdir_or_exist(osp.abspath(cfg.workdir))
    # dump config
    #cfg.dump(osp.join(cfg.workdir, osp.basename(args.config)))
    shutil.copy(args.config, cfg.workdir)
    # init the logger before other steps
    timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    log_file = osp.join(cfg.workdir, f'{timestamp}.log')
    logger = get_root_logger(log_file=log_file, log_level=cfg.log_level)

    print('local_rank', args.local_rank)

    trainval(cfg, args.launcher, logger)


if __name__ == '__main__':
    main()
