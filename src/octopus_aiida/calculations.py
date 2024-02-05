from aiida.common import datastructures
from aiida.engine import CalcJob
from aiida.orm import AbstractCode, SinglefileData


class OctopusCalculation(CalcJob):
    """AiiDA calculation plugin wrapping the Octopus executable."""

    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        super(OctopusCalculation, cls).define(spec)

        # new ports
        spec.input('inp', valid_type=SinglefileData, help='Octopus input file')
        spec.output('octopus', valid_type=SinglefileData, help='Run Octopus DFT code')

        # Capture stdout
        # Need to extend this to folders/more outputs
        spec.input('metadata.options.output_filename', valid_type=str, default='oct.stdout')
        spec.input('code', valid_type=AbstractCode, help='The Octopus binary')

        # Start with serial execution
        spec.inputs['metadata']['options']['resources'].default = {
            'num_machines': 1,
            'num_mpiprocs_per_machine': 1,
        }

        # Note that the default is not set to the Parser class itself, but to the entry point string under which the
        # parser class is registered. We will r
        spec.inputs['metadata']['options']['parser_name'].default = 'octopus-gs'

        # Error codes: https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/processes/usage.html#topics-processes-usage-exit-code-conventions
        # 300 - 399: Suggested for critical process errors
        spec.exit_code(
            300, 'ERROR_MISSING_OUTPUT_FILES', message='Calculation did not produce all expected output files.'
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
        # Files required to run the code - might consider the PPs as well
        calcinfo.local_copy_list = [
            (self.inputs.inp.uuid, self.inputs.inp.filename, self.inputs.inp.filename)
        ]
        # Output files, including stdout, to copy back
        calcinfo.retrieve_list = [self.metadata.options.output_filename]

        return calcinfo
