#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Train a detection model from a set of preprocessed rasters and a vector file of
polygons.

"""
from __future__ import absolute_import, division, print_function

import argparse
import configparser
import logging
import sys
import tempfile

import fiona
import rasterio

from aplatam import __version__
from aplatam.build_trainset import build_trainset
from aplatam.util import all_raster_files

__author__ = "Dymaxion Labs"
__copyright__ = __author__
__license__ = "new-bsd"

_logger = logging.getLogger(__name__)


def parse_args(args):
    """
    Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace

    """
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument(
        '--version',
        action='version',
        version='aplatam {ver}'.format(ver=__version__))

    parser.add_argument(
        'rasters_dir', help='directory containing raster images')
    parser.add_argument('vector', help='vector file of polygons')
    parser.add_argument(
        '-c',
        '--config-file',
        default="default.cfg",
        help='configuration file')
    parser.add_argument(
        '-o',
        '--output-model',
        default='model.h5',
        help='filename for output model')
    parser.add_argument(
        '--seed', type=int, help='seed number for the random number generator')

    parser.add_argument(
        "--temp-dir",
        default=tempfile.gettempdir(),
        help='path to temporary files')

    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):
    """
    Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages

    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel,
        stream=sys.stdout,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """
    Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list

    """
    args = parse_args(args)
    setup_logging(args.loglevel)

    config = read_config_file(args.config_file)

    _logger.debug('Collect all rasters')
    rasters = all_raster_files(args.rasters_dir)

    validate_rasters_band_count(rasters)

    build_trainset(rasters, args.vector, config, temp_dir=args.temp_dir)

    _logger.info('Done')


def get_vector_crs(vector_path):
    """Return CRS of +vector_path+"""
    with fiona.open(vector_path) as dataset:
        return dataset.crs


def validate_rasters_band_count(rasters):
    """
    Validates all rasters have a count of 4 bands

    Returns True if they are all valid.
    Otherwise it raises a RuntimeError.

    """
    _logger.debug('Validate rasters band count')
    for raster_path in rasters:
        count = get_raster_band_count(raster_path)
        if count != 4:
            raise RuntimeError(
                'Rasters must have exactly 4 bands (was {})'.format(count))
    return True


def get_raster_band_count(raster_path):
    """Return band count of +raster_path+"""
    with rasterio.open(raster_path) as dataset:
        return dataset.count


def read_config_file(config_file):
    """
    Reads a +config_file+, parses it and
    returns a dictionary of key-value options

    """
    _logger.debug('read config file')
    config = configparser.ConfigParser()
    config.read(config_file)
    return dict(config['train'])


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
