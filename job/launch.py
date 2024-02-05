"""Launch a calculation using the 'diff-tutorial' plugin"""
from pathlib import Path

from aiida import engine, orm
from aiida.common.exceptions import NotExistent

DIR = Path(__file__).resolve().parent


# Create or load code
computer = orm.load_computer('localhost')
try:
    code = orm.load_code('octopus-gs@localhost')
except NotExistent:
    # Setting up code via python API (or use "verdi code setup")
    code = orm.InstalledCode(
        label='octopus',
        computer=computer,
        filepath_executable='/home/aiida/octopus/cmake-build-release/octopus',
        default_calc_job_plugin='octopus-gs'
    )

# Set up inputs
builder = code.get_builder()
builder.inp = orm.SinglefileData(file=DIR / 'inp')
builder.metadata.description = 'Test job submission with the aiida Octopus plugin'

# Run the calculation & parse results
result = engine.run(builder)
out = result['octopus'].get_content()

print('Octopus output:')
print(out)
