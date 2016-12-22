from pyciss import meta


def test_get_meta_df():
    df = meta.get_meta_df()
    assert df.index[0] == "N1467345444"
    assert not df.iloc[-1]['is_lit']


def test_get_order():
    # This fishes out the resonance order from the identifier string
    # The order is defined as the delta between 1st and 2nd number.
    in_ = "Mimas 4:1"
    expected = 3
    assert meta.get_order(in_) == expected


def test_get_resonances():
    # test if the reading of resonance file works
    df = meta.get_resonances()
    assert df.iloc[0]['name'] == 'Titan 2:0'
    assert df.iloc[-1]['order'] == 3


def test_get_prime_resonances():
    # test if this filters for prime resonances (order = 1)
    df = meta.get_prime_resonances()
    assert meta.get_order(df.iloc[0]['name']) == 1
    assert meta.get_order(df.iloc[-1]['name']) == 1


def test_get_janus_epimetheus_resonances():
    # read higher precision Janus and Epimetheus resonance file
    df = meta.get_janus_epimetheus_resonances()
    assert df.iloc[0]['name'] == 'Janus1 2:1'
    assert df.iloc[-1]['name'] == 'Epimetheus2 15:13'


def test_get_prime_jan_epi():
    # read and filter for prime resonances of Janus and Epimetheus
    df = meta.get_prime_jan_epi()
    assert df.iloc[0]['name'] == 'Janus1 2:1'
    assert df.iloc[-1]['name'] == 'Epimetheus2 7:6'


def test_get_all_resonances():
    # read all moon resonances and merge them into one
    df = meta.get_all_resonances()
    assert df.iloc[0]['name'] == 'Titan 1:0'
    assert df.iloc[-1]['name'] == 'Mimas 3:2'
