from builtins import object
import setup_paths
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.simple_parser import mainFunction, AncillaryParser, CachingLevel
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
import os, sys, json
import fleur_parser_inp
import fleur_XML_parser

################################################################
# This is the parser for the main output file of Fleur (out)
################################################################


class FleurContext(object):
    """context for the fleur parser"""

    def __init__(self):
        self.parser = None
        self.secMethodIndex = None
        self.secSystemIndex = None       

    def initialize_values(self):
        """allows to reset values if the same superContext is used to parse different files"""
       # pass
    
#        self.metaInfoEnv = self.parser.parserBuilder.metaInfoEnv
        self.secMethodIndex = None
        self.secSystemIndex = None
        self.scfIterNr = 0


    def startedParsing(self, path, parser):
        """called when parsing starts"""
        self.parser = parser
        self.metaInfoEnv = self.parser.parserBuilder.metaInfoEnv

        # allows to reset values if the same superContext is used to parse different files
        self.initialize_values()

    def onClose_x_fleur_header(self, backend, gIndex, section):
        backend.addValue("program_version",
                         section["x_fleur_version"][0])


    def onOpen_section_system(self, backend, gIndex, section):
        mainFile = self.parser.fIn.fIn.name
        fName = mainFile[:-4] + ".inp"
        if os.path.exists(fName):
            structSuperContext = fleur_parser_inp.FleurInpContext()
            structParser = AncillaryParser(
                fileDescription = fleur_parser_inp.buildStructureMatchers(),
                parser = self.parser,
                cachingLevelForMetaName = fleur_parser_inp.get_cachingLevelForMetaName(self.metaInfoEnv, CachingLevel.PreOpenedIgnore),
                superContext = inpSuperContext)

            with open(fName) as fIn:
                inpParser.parseFile(fIn)



    def onOpen_section_system(self, backend, gIndex, section):
        mainFile = self.parser.fIn.fIn.name
        fName = mainFile[:-4] + ".xml"
        if os.path.exists(fName):
            xmlSuperContext = fleur_parser_xml.FleurXmlContext()
            xmlParser = AncillaryParser(
                fileDescription = fleur_parser_xml.buildXmlMatchers(),
                parser = self.parser,
                cachingLevelForMetaName = fleur_parser_xml.get_cachingLevelForMetaName(self.metaInfoEnv, CachingLevel.PreOpenedIgnore),
                superContext = xmlSuperContext)

            with open(fName) as fXml:
                xmlParser.parseFile(fXml)


    def onClose_section_single_configuration_calculation(self, backend, gIndex, section):
        """Trigger called when section_single_configuration_calculation is opened.
        """
        # write number of SCF iterations
        backend.addValue('number_of_scf_iterations', self.scfIterNr)
        
        # write the references to section_method and section_system
        #        method_index = self.secMethodIndex("single_configuration_to_calculation_method_ref")
        #        if method_index is not None:
        
        backend.addValue('single_configuration_to_calculation_method_ref', self.secMethodIndex)
        #        system_index = self.secSystemIndex("single_configuration_calculation_to_system_ref")
        #        if system_index is not None:
                
        backend.addValue('single_configuration_calculation_to_system_ref', self.secSystemIndex)

            
    def onOpen_section_method(self, backend, gIndex, section):
        if self.secMethodIndex is None:
            self.secMethodIndex = gIndex
#        self.secMethodIndex["single_configuration_to_calculation_method_ref"] = gIndex


    def onOpen_section_system(self, backend, gIndex, section):
        if self.secSystemIndex is None:        
            self.secSystemIndex = gIndex
#        self.secSystemIndex["single_configuration_calculation_to_system_ref"] = gIndex    

   
    def onClose_section_scf_iteration(self, backend, gIndex, section):
        #Trigger called when section_scf_iteration is closed.
        
        # count number of SCF iterations
        self.scfIterNr += 1


    def onClose_x_fleur_section_XC(self, backend, gIndex, section):
        xc_index = section["x_fleur_exch_pot"]
        if not xc_index:
            functional = "pbe"
        if functional:
            xc_map_legend = {

                'pbe': ['GGA_X_PBE', 'GGA_C_PBE'],

                'rpbe': ['GGA_X_PBE', 'GGA_C_PBE'],

                'Rpbe': ['GGA_X_RPBE'],
                
                'pw91': ['GGA_X_PW91','GGA_C_PW91'],
                
                'l91': ['LDA_C_PW','LDA_C_PW_RPA','LDA_C_PW_MOD','LDA_C_OB_PW'],

                'vwn': ['LDA_C_VWN','LDA_C_VWN_1','LDA_C_VWN_2','LDA_C_VWN_3','LDA_C_VWN_4','LDA_C_VWN_RPA'],

                'bh': ['LDA_C_VBH'],

                'pz':['LDA_C_PZ'],

                'x-a': [],

                'mjw': [],

                'wign': [],

                'hl': [],

                'xal': [],

                'relativistic': ['---']
            #http://dx.doi.org/10.1088/0022-3719/12/15/007

            }
    
            # Push the functional string into the backend
            nomadNames = xc_map_legend.get(functional)
            if not nomadNames:
                raise Exception("Unhandled xc functional %s found" % functional)

            for xc_name in nomadNames:
                s = backend.openSection("section_XC_functionals")
                backend.addValue("XC_functional_name", xc_name)
                backend.closeSection("section_XC_functionals", s)

#*

#    def onClose_section_run(self, backend, gIndex, section):
#        """Trigger called when section_run is closed.
#        """
        # reset all variables
#        self.initialize_values()
#        backend.addValue("energy_total", energy_total)
#        # frame sequence
#        sampling_method = "geometry_optimization"

#        samplingGIndex = backend.openSection("section_sampling_method")
#        backend.addValue("sampling_method", sampling_method)
#        backend.closeSection("section_sampling_method", samplingGIndex)
#        frameSequenceGIndex = backend.openSection("section_frame_sequence")
#        backend.addValue("frame_sequence_to_sampling_ref", samplingGIndex)
#        backend.addArrayValues("frame_sequence_local_frames_ref", np.asarray(self.singleConfCalcs))
#        backend.closeSection("section_frame_sequence", frameSequenceGIndex)



"""    def onClose_x_fleur_section_xml_file(self, backend, gIndex, section):

        x_fleur_loading_xml_file_list = section['x_fleur_loading_xml_file']

        xml_file = x_fleur_loading_xml_file_list[-1]        
 
        if xml_file is not None: 
           logger.warning("This output showed this calculation need to load xml file, so we need this xml file ('%s') to read geometry information" % os.path.normpath(xml_file) )
           fName = os.path.normpath(xml_file)

           xmlSuperContext = FleurXMLParser.FleurXMLParserContext(False)
           xmlParser = AncillaryParser(
                fileDescription = FleurXMLParser.build_FleurXMLFileSimpleMatcher(),
                parser = self.parser,
                cachingLevelForMetaName = FleurXMLParser.get_cachingLevelForMetaName(self.metaInfoEnv, CachingLevel.Ignore),
                superContext = xmlSuperContext)

           try:
                with open(fName) as fxml:
                     xmlParser.parseFile(fxml)
          
           except IOError:
                logger.warning("Could not find xml file in directory '%s'. " % os.path.dirname(os.path.abspath(self.fName)))
"""
"""
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

"""

#####################################################################################################
#                                          description of the input                                 #
#####################################################################################################

mainFileDescription = SM(
              name = 'root',
              weak = True,
              startReStr = "",
              subMatchers = [
                SM(name = 'newRun',
                startReStr = r"\s* This output is generated by\s*[\w*.]+\s*\w*\*\s\*",
                repeats = True,
                required = True,
                forwardMatch = True,
                   sections   = ['section_run','section_method', 'section_system', 'section_single_configuration_calculation'],
                subMatchers = [
### header ###
                SM(name = 'header',
                  startReStr = r"\s* This output is generated by\s*(?P<x_fleur_version>[\w*.]+)\s*\w*\*\s\*",
                  sections=["x_fleur_header"],
                  fixedStartValues={'program_name': 'Fleur', 'program_basis_set_type': 'FLAPW' }
                  ),
                    
                 SM(name = 'systemName',
                    startReStr = r"\s*strho.*\n(?P<x_fleur_system_name>.*)",#L14
                    sections = ["section_system"],
                    subMatchers=[
                        SM(r"\s*the volume of the unit cell omega=\s*(?P<x_fleur_unit_cell_volume_omega>[0-9.]+)"), #L136
                        SM(r"\s*the volume of the unit cell omega-tilda=\s*(?P<x_fleur_unit_cell_volume>[0-9.]+)"),#L137
#                        SM(r"\s*exchange-correlation:\s*(?P<x_fleur_exch_pot>\w*\s*.*)",sections = ['x_fleur_section_XC']), #L140
                        SM(r"\s*exchange-correlation:\s*(?P<x_fleur_exch_pot>\w*)\s*(?P<x_fleur_xc_correction>\w*\s*.*)",sections = ['x_fleur_section_XC']), #L140
                        SM(r"\s* Suggested values for input:"),
                        SM(r"\s*k_max\s=\s*(?P<x_fleur_k_max>.*)"),#L154
                        SM(r"\s*G_max\s=\s*(?P<x_fleur_G_max>.*)"),#L155
                        SM(r"\s*volume of interstitial region=\s*(?P<x_fleur_vol_interstitial>[0-9.]+)"),#L157
                        SM(r"\s*number of atom types=\s*(?P<x_fleur_nr_of_atom_types>[0-9]+)"),#L160
                        SM(r"\s*total number of atoms=\s*(?P<x_fleur_total_atoms>[0-9]+)"),

                        SM(r"\s*(?P<x_fleur_smearing_kind>\w*)-integration is used\s*.*"),#L187
                        SM(r"\s*gaussian half width\s*=\s*(?P<x_fleur_smearing_width>[0-9.]+)"),#188
                        SM(r"\s*number of valence electrons=\s*(?P<x_fleur_nr_of_valence_electrons>[0-9.]+)"),#190
                        SM(r"\s*temperature broadening\s*=\s*(?P<x_fleur_smearing_temperature>[0-9.]+)"),#191

                        SM(r"\s*total electronic charge   =\s*(?P<x_fleur_tot_elec_charge>.*)"),#L1107
                        SM(r"\s*total nuclear charge      =\s*(?P<x_fleur_tot_nucl_charge>.*)") #L1108

                    ]),
            
                SM(
                      name = "scf iteration",
                      startReStr = r"\s*it=       \s*(?P<x_fleur_iteration_number>[0-9]+)",
                      sections=["section_scf_iteration"],
                      repeats = True,
                      subMatchers=[
                               SM(r"---->\s*total energy=\s*(?P<x_fleur_energy_total>[-+0-9.]+)")
                      ]
                    )
                ])
              ])

# which values to cache or forward (mapping meta name -> CachingLevel)

cachingLevelForMetaName = {

    "XC_functional_name": CachingLevel.ForwardAndCache,
    "energy_total": CachingLevel.ForwardAndCache
    
 }
# loading metadata from nomad-meta-info/meta_info/nomad_meta_info/fleur.nomadmetainfo.json

parserInfo = {
  "name": "Fleur_parser",
  "version": "1.0"
}

metaInfoPath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"../../../../nomad-meta-info/meta_info/nomad_meta_info/fleur.nomadmetainfo.json"))
metaInfoEnv, warnings = loadJsonFile(filePath = metaInfoPath, dependencyLoader = None, extraArgsHandling = InfoKindEl.ADD_EXTRA_ARGS, uri = None)

if __name__ == "__main__":
    superContext = FleurContext()
    mainFunction(mainFileDescription, metaInfoEnv, parserInfo, superContext = superContext)
