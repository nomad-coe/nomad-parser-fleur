from builtins import object
import setup_paths
from nomadcore.simple_parser import mainFunction, CachingLevel
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
import os, sys, json, logging
import numpy as np


################################################################
# This is the subparser for the main fleur input file (.inp)
################################################################


class FleurInpContext(object):
    """context for wien2k struct parser"""

    def __init__(self):
        self.parser = None

    def initialize_values(self):
        """allows to reset values if the same superContext is used to parse different files"""
        pass

    def startedParsing(self, path, parser):
        """called when parsing starts"""
        self.parser = parser
        # allows to reset values if the same superContext is used to parse different files
        self.initialize_values()

    def onClose_section_system(self, backend, gIndex, section):
        equiv_atoms = section["x_fleur_section_equiv_atoms"]
        #logging.error("section: %s", section)
        labels = []
        pos = []
        for eqAtoms in equiv_atoms:
            label = eqAtoms["x_fleur_atom_name"][0]
            x = eqAtoms["x_fleur_atom_pos_x"]
            y = eqAtoms["x_fleur_atom_pos_y"]
            z = eqAtoms["x_fleur_atom_pos_z"]
            if len(x) != len(y) or len(x) != len(z):
                raise Exception("incorrect parsing, different number of x,y,z components")
            groupPos = [[x[i],y[i],z[i]] for i in range(len(x))]
            nAt = len(groupPos)
            labels += [label for i in range(nAt)]
            pos += groupPos
        backend.addValue("atom_labels", labels)
        backend.addValue("atom_positions", pos)


# description of the input
def buildStructureMatchers():
    return SM(
    name = 'root',
    weak = True,
    startReStr = "",
    sections = ["section_run", "section_system"],
    subMatchers = [
        SM(name = 'systemName',
           startReStr = r"\s*strho.*\n(?P<x_fleur_system_nameIn>.*)"),#L2
        SM(r"\s{2}(?P<<x_fleur_nr_of_atom_types>[0-9]+)\n",#L10
#
           sections=["x_fleur_section_equiv_atoms"],
           subMatchers=[
               SM(r"\W{35}\n*(?P<x_fleur_name_of_atom_type>\w*)\s*(?P<x_fleur_nuclear_number>[0-9].*)\s(?P<x_fleurnumber_of_core_levels>[0-9].*)\s*(?P<l-expansion_cutoff>[0-9].)\s(?P<x_fleur_mt_gridpoints>[0-9].*)\s(?P<x_fleur_mt_radius>[0-9].+)\s(?P<x_fleur_logarythmic_increment>[0-9].*)"),#l11
               SM(r"(?P<number_equiv_atoms_in_this_atom_type>[0-9].*),force\s=.*"),# number of equivalent atoms in this atom type
               SM(r"\s*force.*\n\s*(?P<x_fleur_atom_pos_x>[-+0-9.]+)\s+(?P<x_fleur_atom_pos_y>[-+0-9.]+)\s+(?P<x_fleur_atom_pos_z>[-+0-9.]+)\s+(?P<x_fleur_atom_coord_scale>[-+0-9.]+)\n",
                  repeats=True,
                  )
                        ],
               repeat = True
        # SM(r"\s\s(?P<add>[0-9.]*)\s\s(?P<addd>[0-9.]*)\nvchk.*"),  
       )
    ])

def get_cachingLevelForMetaName(metaInfoEnv, CachingLvl):
    """Sets the caching level for the metadata.

    Args:
        metaInfoEnv: metadata which is an object of the class InfoKindEnv in nomadcore.local_meta_info.py.
        CachingLvl: Sets the CachingLevel for the sections k_band, run, and single_configuration_calculation.
            This allows to run the parser without opening new sections.

    Returns:
        Dictionary with metaname as key and caching level as value.
    """
    # manually adjust caching of metadata
    cachingLevelForMetaName = {
                               'section_run': CachingLvl,
                               'section_system': CachingLvl
                              }
    cachingLevelForMetaName["x_fleur_system_nameIn"] = CachingLevel.ForwardAndCache
    cachingLevelForMetaName["x_fleur_section_equiv_atoms"] = CachingLevel.ForwardAndCache
    return cachingLevelForMetaName

# loading metadata from nomad-meta-info/meta_info/nomad_meta_info/fhi_aims.nomadmetainfo.json
