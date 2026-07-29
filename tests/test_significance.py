from intelligence.significance import binomial_significance_test, is_significant_anomaly


def test_identical_rate_is_not_significant():
    p_value = binomial_significance_test(15, 100, 0.15)
    assert p_value > 0.05


def test_extreme_deviation_is_significant():
    p_value = binomial_significance_test(0, 100, 0.15)
    assert p_value < 0.05


def test_is_significant_anomaly_returns_correct_boolean():
    significant, p_value = is_significant_anomaly(0, 200, 0.15)
    assert significant == True

    significant, p_value = is_significant_anomaly(30, 200, 0.15)
    assert significant == False