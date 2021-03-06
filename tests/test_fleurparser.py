#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest

from nomad.datamodel import EntryArchive
from fleurparser import FleurParser


def approx(value, abs=0, rel=1e-6):
    return pytest.approx(value, abs=abs, rel=rel)


@pytest.fixture(scope='module')
def parser():
    return FleurParser()


def test_basic(parser):
    archive = EntryArchive()

    parser.parse('tests/data/Si/out', archive, None)

    sec_run = archive.section_run[0]
    assert sec_run.program_version == 'fleur.26b'

    sec_system = archive.section_run[0].section_system[0]
    assert sec_system.lattice_vectors[1][2].magnitude == approx(2.73444651e-10)
    assert sec_system.atom_labels == ['Si', 'Si']
    assert sec_system.atom_positions[1][2].magnitude == approx(-6.97283857e-11)

    sec_sccs = sec_run.section_single_configuration_calculation
    assert len(sec_sccs) == 20
    assert sec_sccs[18].energy_total.magnitude == approx(-2.52896385e-15)
    assert sec_sccs[4].energy_free.magnitude == approx(-2.52896386e-15)
    assert sec_sccs[9].atom_forces[1][1].magnitude == approx(7.34976523e-10)

