import numpy as np
import pytest
from aiida import engine, orm

CODE_LABEL = 'octopus-gs@localhost'
CALC_JOB_PLUGIN = 'octopus.ground_state'

INPUT_STRING = """
CalculationMode = gs
ExperimentalFeatures = yes
FromScratch = yes

Dimensions = 3

%Coordinates
"C"  | -1.24513 |  -2.28661 |  7.53205
"C"  |  1.39385 |  -2.28661 |  7.60583
"C"  | -2.56491 |  -0.00011 |  7.49979
"C"  |  2.71444 |  -0.00008 |  7.63775
"C"  | -1.24514 |   2.28648 |  7.53208
"C"  |  1.39384 |   2.28648 |  7.60586
"H"  | -2.27540 |  -4.07521 |  7.51055
"H"  |  2.42510 |  -4.07517 |  7.62123
"H"  | -4.62544 |  -0.00011 |  7.45697
"H"  |  4.77899 |  -0.00008 |  7.67882
"H"  | -2.27542 |   4.07503 |  7.51060
"H"  |  2.42508 |   4.07502 |  7.62128
%

Radius = 3.5 * angstrom
Spacing = 0.18 * angstrom

XCFunctional = lda_x + lda_c_pz

# Speed up for testing purposes
MaximumIter = 3
"""


@pytest.fixture
def gs_builder(aiida_create_or_load_code, tmp_path):
    code = aiida_create_or_load_code(CODE_LABEL, CALC_JOB_PLUGIN)
    builder = code.get_builder()
    input_path = tmp_path / 'inp'
    input_path.write_text(INPUT_STRING)
    builder.inp = orm.SinglefileData(file=input_path)
    return builder


def test_gs_molecule(gs_builder):
    builder = gs_builder
    builder.metadata.description = test_gs_molecule.__name__
    result = engine.run(builder)

    convergence = result['convergence'].get_dict()
    assert len(convergence['energy']) == 3, 'Expect an initial guess plus 2 SCF steps'
    assert np.isclose(convergence['energy']['3'], -48.9235416)

    forces = result['forces'].get_dict()
    assert forces['nl_x'] == {'1': 0.0648884067, '2': -0.0631829402, '3': 0.12434277, '4': -0.125716715, '5': 0.0649128124,
                              '6': -0.0631950874, '7': 0.0, '8': 0.0, '9': 0.0, '10': 0.0, '11': 0.0, '12': 0.0}
    assert forces['scf_z'] == {'1': -0.00568797351, '2': 0.00295226342, '3': -0.00757471667, '4': 0.00602384034,
                               '5': -0.005685597, '6': 0.00295777309, '7': -0.00113953409, '8': 0.000989301227,
                               '9': -0.00225415002, '10': 0.0021264027, '11': -0.00113863621, '12': 0.000990155991}
