#!/usr/bin/env python
# -*- coding: utf-8

import os
import pandas as pd

import anvio
import anvio.terminal as terminal
import anvio.constants as constants
import anvio.filesnpaths as filesnpaths

from anvio.errors import ConfigError
from anvio.parsers.base import Parser


__author__ = "Developers of anvi'o (see AUTHORS.txt)"
__copyright__ = "Copyleft 2015-2018, the Meren Lab (http://merenlab.org/)"
__credits__ = []
__license__ = "GPL 3.0"
__version__ = anvio.__version__
__maintainer__ = "Matthew S. Schechter"
__email__ = "mschechter@uchicago.edu"


class Agnostos(Parser):
    def __init__(self, input_file_paths, run=terminal.Run(), progress=terminal.Progress()):
        self.run = run
        self.progress = progress
        self.just_do_it = False

        input_file_path = self.fix_input_file(input_file_paths[0])

        files_expected = {'agnostos_output': input_file_path}

        files_structure = {'agnostos_output':
                                {'col_names': ['gene_callers_id', 'cl_name', 'contig', 'gene_x_contig', 'db', 'cl_size', 'category', 'is.HQ', 'is.LS', 'lowest_rank', 'lowest_level', 'niche_breadth_sign'],
                                 'col_mapping': [int,                 str,     str,         str,        str,   str,        str,        str,    str,       str,            str,           str],
                                 'indexing_field': -1,
                                 'separator': '\t'},
                            }

        Parser.__init__(self, 'agnostos', [input_file_path], files_expected, files_structure)

        # This is where I would specific sanity checks for agnostos

    def fix_input_file(self, input_file_path):
        """Select columns for anvio and remove duplicate rows"""
        self.progress.new('Making agnostos output anvio friendly')
        self.progress.update('...')

        temp_file_path = filesnpaths.get_temp_file_path()


        df = pd.read_csv(input_file_path, sep='\t')
        df = df[["gene_callers_id", "cl_name", "contig", "gene_x_contig", "db", "cl_size", "category", "is.HQ", "is.LS", "lowest_rank", "lowest_level", "niche_breadth_sign"]]
        df = df.drop_duplicates(subset=["gene_callers_id"])

        df.to_csv(temp_file_path, sep = '\t', index = False, na_rep = 'NA')

        self.progress.end()

        return temp_file_path


    def get_dict(self):
        """Convert angostos output into functions dict"""
        d = self.dicts['agnostos_output']

        # Parse Agnostos output to make functions_dict
        df = pd.DataFrame.from_dict(d, orient='index')
        df['source'] = "Agnostos"
        df['e_value'] = 0
        df.rename(columns = {'cl_name':'accession'}, inplace = True)
        df.rename(columns = {'category':'function'}, inplace = True)
        df = df.drop_duplicates(subset=['gene_callers_id', 'source', 'accession', 'function'])
        d = df.to_dict(orient='index')

        return d
