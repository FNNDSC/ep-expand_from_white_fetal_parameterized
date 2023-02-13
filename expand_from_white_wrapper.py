#!/usr/bin/env python
import os
import subprocess as sp
import sys
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

from chris_plugin import chris_plugin, PathMapper
from loguru import logger

__version__ = '1.0.0'

parser = ArgumentParser(description='ChRIS plugin wrapper around a modified expand_from_white',
                        formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument('-l', '--laplacian-weight-coefficient', type=str, required=True, dest='lw',
                    help='Laplacian weight coefficient')
parser.add_argument('-s', '--stretch-weight-coefficient', type=str, required=True, dest='sw',
                    help='Stretch weight coefficient')
parser.add_argument('--side', type=str, default='auto',
                    help='brain hemisphere, one of: left, right, auto')

parser.add_argument('-t', '--threads', type=int, default=0,
                    help='Number of threads to use for parallel jobs. '
                         'Pass 0 to use number of visible CPUs.')
parser.add_argument('--no-fail', dest='no_fail', action='store_true',
                    help='Produce exit code 0 even if any subprocesses do not.')
parser.add_argument('-V', '--version', action='version',
                    version=f'%(prog)s {__version__}')


@chris_plugin(
    parser=parser,
    title='expand_from_white fetus CP experiment',
    category='Experiment',
    min_memory_limit='1Gi',
    min_cpu_limit='1000m',
    min_gpu_limit=0
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    if options.threads > 0:
        nproc = options.threads
    else:
        nproc = len(os.sched_getaffinity(0))
    logger.info('Using {} threads.', nproc)

    mapper = PathMapper.file_mapper(inputdir, outputdir, glob='**/*.mnc', suffix='.obj')
    with ThreadPoolExecutor(max_workers=nproc) as pool:
        results = pool.map(lambda t: run_surface_fit(*t, options.side, options.sw, options.lw), mapper)

    if not options.no_fail and not all(results):
        sys.exit(1)


def run_surface_fit(grid: Path, output_surf: Path, given_side: str, sw: str, lw: str) -> bool:
    """
    :return: True if successful
    """
    starting_surface = locate_surface_for(grid)
    if starting_surface is None:
        logger.error('No starting surface found for {}', grid)
        return False

    side = select_side(given_side, grid)
    cmd = ['expand_from_white_fetal_MNI.pl', side, starting_surface, output_surf, grid, sw, lw]
    log_file = output_surf.with_name(output_surf.name + '.log')
    logger.info('Starting: {}', ' '.join(map(str, cmd)))
    with log_file.open('wb') as log_handle:
        job = sp.run(cmd, stdout=log_handle, stderr=log_handle)
    rc_file = log_file.with_suffix('.rc')
    rc_file.write_text(str(job.returncode))

    if job.returncode == 0:
        logger.info('Finished: {} -> {}', starting_surface, output_surf)
        return True

    logger.error('FAILED -- check log file for details: {}', log_file)
    return False


def select_side(given_side: str, input_path: Path):
    if given_side != 'auto':
        return f'-{given_side}'
    lower_path = str(input_path).lower()
    if 'left' in lower_path:
        return '-left'
    if 'right' in lower_path:
        return '-right'
    raise ValueError(f'Cannot determine side for {input_path}')


def locate_surface_for(mask: Path) -> Optional[Path]:
    glob = mask.parent.glob('*.obj')
    first = next(glob, None)
    second = next(glob, None)
    if second is not None:
        return None
    return first


if __name__ == '__main__':
    main()
