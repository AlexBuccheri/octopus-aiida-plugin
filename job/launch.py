"""Launch an Octopus calculation"""
import numpy as np
from aiida import engine, orm
from aiida.common.exceptions import NotExistent

from octopus_aiida import PROJECT_ROOT


PRINT_OUT = False

# Create or load code
CODE_LABEL = 'octopus-gs@localhost'
computer = orm.load_computer('localhost')
try:
    code = orm.load_code(CODE_LABEL)
except NotExistent:
    code = orm.InstalledCode(
        label='octopus-gs',
        computer=computer,
        filepath_executable='/lib/octopus/release-serial/bin/octopus',
        default_calc_job_plugin='octopus.ground_state'
    ).store()

# Set up inputs
builder = code.get_builder()
# Input string generation can be included here
builder.inp = orm.SinglefileData(file=PROJECT_ROOT / 'job/inp')
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

# Assert on some arbitrary data fields
convergence = result['convergence'].get_dict()
assert len(convergence['energy']) == 3, 'Expect an initial guess plus 2 SCF steps'
assert np.isclose(convergence['energy']['3'], -48.9235416)

forces = result['forces'].get_dict()
assert forces['nl_x'] == {'1': 0.0648884067, '2': -0.0631829402, '3': 0.12434277, '4': -0.125716715, '5': 0.0649128124,
                          '6': -0.0631950874, '7': 0.0, '8': 0.0, '9': 0.0, '10': 0.0, '11': 0.0, '12': 0.0}
assert forces['scf_z'] == {'1': -0.00568797351, '2': 0.00295226342, '3': -0.00757471667, '4': 0.00602384034,
                           '5': -0.005685597, '6': 0.00295777309, '7': -0.00113953409, '8': 0.000989301227,
                           '9': -0.00225415002, '10': 0.0021264027, '11': -0.00113863621, '12': 0.000990155991}

if PRINT_OUT:
    print('Convergence:')
    for key, val in convergence.items():
        print(key, val)
    print()
    print('Forces:')
    for key, val in forces.items():
        print(key, val)
