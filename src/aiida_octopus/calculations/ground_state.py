from aiida.common import datastructures
from aiida.engine import CalcJob
from aiida.orm import AbstractCode, SinglefileData, Dict


class OctopusGSCalculation(CalcJob):
    """AiiDA calculation plugin wrapping the Octopus executable
    for a ground state calculation."""

    # TODOs
    # * Add info to the spec and the retrieve_list

    _OCT_FINISHED = 'exec/oct-status-finished'
    _INPUT_FILE = 'inp'
    _CONVERGENCE_FILE = 'static/convergence'
    _FORCES_FILE = 'static/forces'
    _INFO_FILE = 'static/info'

    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        super(OctopusGSCalculation, cls).define(spec)

        spec.input('code', valid_type=AbstractCode, help='The Octopus binary')
        spec.input('inp', valid_type=SinglefileData, help='Octopus input file')

        # Std-out output_filename
        spec.input('metadata.options.output_filename', valid_type=str, default='oct.stdout')
        # Node to attach std-out to via output_filename (specified in OctopusGSParser)
        spec.output('octopus', valid_type=SinglefileData, required=False)

        # static/ outputs
        spec.output('convergence', valid_type=Dict, required=False)
        spec.output('forces', valid_type=Dict, required=False)

        # Default = Serial execution
        spec.inputs['metadata']['options']['resources'].default = {
            'num_machines': 1,
            'num_mpiprocs_per_machine': 1,
        }

        # Note that the default is not set to the Parser class itself,
        # but to the entry point module string where the parser class is defined.
        # This is specified in pyproject.toml
        spec.inputs['metadata']['options']['parser_name'].default = 'octopus.ground_state'

        # Error codes: https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/processes/usage.html#topics-processes-usage-exit-code-conventions
        # 300 - 399: Suggested for critical process errors
        spec.exit_code(
            300, 'ERROR_MISSING_OUTPUT_FILES', message='Calculation did return any output files.'
        )
        spec.exit_code(
            301, 'ERROR_CALCULATION_NOT_FINISHED', message='Calculation did not exit cleanly.'
        )
        spec.exit_code(
            310, 'ERROR_PARSING_CONVERGENCE', message='Failed to parse static/convergence.'
        )
        spec.exit_code(
            311, 'ERROR_PARSING_FORCES', message='Failed to parse static/forces.'
        )

    def prepare_for_submission(self, folder):
        """Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        Any files created in folder will be copied for the calculation run,

        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        codeinfo = datastructures.CodeInfo()
        # No cmd line params required required
        codeinfo.cmdline_params = []
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]

        # Files required to run the code
        # (node_uuid, source_path_inside_node, target_path_on_remote)
        calcinfo.local_copy_list = [
            (self.inputs.inp.uuid, self.inputs.inp.filename, self._INPUT_FILE)
        ]

        # Output files, including stdout, to copy back
        # Files should be consistent with those defined in the parser
        # 3rd entry defines the file's nesting level w.r.t. run directory
        calcinfo.retrieve_list = [
            self.metadata.options.output_filename,
            (self._OCT_FINISHED, '.', 2),
            (self._CONVERGENCE_FILE, '.', 2),
            (self._FORCES_FILE, '.', 2)
        ]

        return calcinfo
