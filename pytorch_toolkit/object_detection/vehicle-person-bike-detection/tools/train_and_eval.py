# Copyright (C) 2020 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.

# pylint: disable=no-value-for-parameter

import argparse
import os
import subprocess

import yaml
from mmcv.utils import Config

from eval import main as evaluate


def parse_args():
    """ Parses input args. """

    parser = argparse.ArgumentParser()
    parser.add_argument('config',
                        help='A path to model training configuration file (.py).')
    parser.add_argument('gpu_num',
                        help='A number of GPU to use in training.')
    parser.add_argument('out',
                        help='A path to output file where models metrics will be saved (.yml).')
    parser.add_argument('--update_config',
                        help='Update configuration file by parameters specified here.'
                             'Use quotes if you are going to change several params.',
                        default='')

    return parser.parse_args()


def main():
    """ Main function. """

    args = parse_args()

    mmdetection_tools = f'{os.path.dirname(__file__)}/../../../../external/mmdetection/tools'

    cfg = Config.fromfile(args.config)

    update_config = f' --update_config {args.update_config}' if args.update_config else ''

    subprocess.run(f'{mmdetection_tools}/dist_train.sh'
                   f' {args.config}'
                   f' {args.gpu_num}'
                   f'{update_config}'.split(' '), check=True)

    overrided_work_dir = [p.split('=') for p in args.update_config.strip().split(' ') if
                          p.startswith('work_dir=')]
    if overrided_work_dir:
        cfg.work_dir = overrided_work_dir[0][1]

    evaluate(args.config, os.path.join(cfg.work_dir, "latest.pth"), args.out, args.update_config)

    with open(args.out, 'r+') as dst_file:
        content = yaml.load(dst_file, Loader=yaml.FullLoader)
        content['training_gpu_num'] = args.gpu_num
        yaml.dump(content, dst_file)


if __name__ == '__main__':
    main()
