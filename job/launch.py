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
        filepath_executable='/lib/octopus/release-serial/bin/octopus',
        default_calc_job_plugin='octopus.static'
    )

# Set up inputs
builder = code.get_builder()
# TODO Add input generation here
builder.inp = orm.SinglefileData(file=DIR / 'inp')
builder.metadata.description = 'Test job submission with the aiida Octopus plugin'

# Run the calculation & parse results
result = engine.run(builder)

# Outputs
nlines = 10
print(f'Last {nlines} lines of Octopus standard output:')
stout: str = result['octopus'].get_content()
lines = stout.splitlines()
for line in lines[-nlines:]:
    print(line)

print('Convergence:')
print(result['convergence'].get_dict())


