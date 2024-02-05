from aiida.engine import ExitCode
from aiida.orm import SinglefileData
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory

OctopusGSCalculation = CalculationFactory('octopus-gs')


class OctopusParser(Parser):
    def parse(self, **kwargs):
        """Parse outputs, store results in database."""
        # Note, 'output_filename' is a key
        output_filename = self.node.get_option('output_filename')

        # Check that folder content is as expected
        files_retrieved = self.retrieved.list_object_names()
        files_expected = [output_filename]
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error(f"Found files '{files_retrieved}', expected to find '{files_expected}'")
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # add output file
        self.logger.info(f"Parsing '{output_filename}'")
        with self.retrieved.open(output_filename, 'rb') as handle:
            output_node = SinglefileData(file=handle)
        self.out('octopus', output_node)

        return ExitCode(0)
