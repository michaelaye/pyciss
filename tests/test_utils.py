from pyciss import _utils as u


def test_which_epi_janus_resonance():
    assert u.which_epi_janus_resonance('Janus', '2005-01-01') == "Janus2"
    assert u.which_epi_janus_resonance('Epimetheus', '2007-01-01') == "Epimetheus1"
    assert u.which_epi_janus_resonance('Janus', '2011-01-01') == "Janus2"
