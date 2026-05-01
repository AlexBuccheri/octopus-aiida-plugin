from __future__ import annotations

from aiida.engine import ExitCode
from aiida.orm import SinglefileData, Dict
from aiida.parsers.parser import Parser

from pandas import DataFrame
from postopus.files import PandasTextFile


class OctopusStaticParser(Parser):
    """Parser for Octopus static/ outputs"""

    _STATIC_FILES = ['convergence', 'forces'] # 'info' not currently set in calculations


    def _check_files(self, output_filename) -> ExitCode | None:
        """ Check files are present

        :param output_filename:
        :return:
        """

        # Calculation did not return any output files
        try:
            files_retrieved = set(self.retrieved.list_object_names())
        except OSError:
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # TODO(Alex) Move this into a OctopusExecParser(Parser)
        # Calculation did not terminate cleanly
        exec_files = set(self.retrieved.list_object_names('exec'))
        if 'oct-status-finished' not in exec_files:
            return self.exit_codes.ERROR_CALCULATION_NOT_FINISHED

        # Presence of std-out
        if output_filename not in files_retrieved:
            self.logger.error(
                f"Missing stdout file '{output_filename}'. "
                f"Top-level retrieved files: {files_retrieved}"
            )
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # Check static/ output directory present
        if 'static' not in files_retrieved:
            self.logger.error(
                f"Missing retrieved 'static' directory. "
                f"Top-level retrieved files: {files_retrieved}"
            )
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # Check files are present in output directory
        static_files = set(self.retrieved.list_object_names('static'))

        for file in self._STATIC_FILES:
            if file not in static_files:
                self.logger.error(
                    f"Missing static/{file}. "
                    f"Files in static/: {static_files}"
                )
                return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        return None

    def read_static(self, name: str) -> DataFrame:
        with self.retrieved.as_path(f"static/{name}") as file_path:
            f = PandasTextFile(file_path)
            data = f.values
            if hasattr(data, "attrs"):
                data.attrs = f.attrs
            return data

    def parse(self, **kwargs):
        """Parse outputs, store results in database."""

        # Std-out
        output_filename = self.node.get_option('output_filename')

        exit_code = self._check_files(output_filename)
        if exit_code is not None:
            return exit_code

        # Store stdout as a raw output node.
        self.logger.info(f"Parsing '{output_filename}'")
        with self.retrieved.open(output_filename, 'rb') as handle:
            self.out('octopus', SinglefileData(file=handle))

        # Parse static/convergence using Postopus module.
        try:
            parsed = self.read_static("convergence")
        except Exception as exc:
            self.logger.exception(f"Failed to parse static/convergence: {exc}")
            return self.exit_codes.ERROR_PARSING_CONVERGENCE

        self.out('convergence', Dict(dict=parsed.to_dict()))

        # TODO Add forces and info

        return ExitCode(0)
