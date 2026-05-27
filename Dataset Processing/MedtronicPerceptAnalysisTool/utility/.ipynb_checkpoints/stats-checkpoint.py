from scipy.stats import ttest_ind, wilcoxon, ranksums, mannwhitneyu, ttest_rel
import itertools


def ttest_independent(data_dict: dict, equal_var=False):

    assert isinstance(data_dict, dict), f"`input` has to be of `dict` type, got {type(data_dict)}"

    result = {}

    pair_combinations = itertools.combinations(data_dict.keys(), 2)

    for item_a, item_b in pair_combinations:
        result[(item_a, item_b)] = ttest_ind(a=data_dict[item_a], b=data_dict[item_b], equal_var=equal_var)

    return result

def ttest_dependent(data_dict: dict, equal_var=False):

    assert isinstance(data_dict, dict), f"`input` has to be of `dict` type, got {type(data_dict)}"

    result = {}

    pair_combinations = itertools.combinations(data_dict.keys(), 2)

    for item_a, item_b in pair_combinations:
        result[(item_a, item_b)] = ttest_rel(a=data_dict[item_a], b=data_dict[item_b], equal_var=equal_var)

    return result


def wilcoxon_paired(data_dict, alternative="two-sided"):
    """Wilcoxon Signed Rank test - Non-parametric paired test

    Used in Adamchic, I., Hauptmann, C., Barnikol, U. B., Pawelczyk, N., Popovych, O., Barnikol, T. T., Silchenko, A., Volkmann, J., Deuschl, G., Meissner, W. G., Maarouf, M., Sturm, V., Freund, H.-J., & Tass, P. A. (2014). Coordinated reset neuromodulation for Parkinson’s disease: Proof-of-concept study. Movement Disorders, 29(13), 1679–1684. https://doi.org/10.1002/mds.25923

    """
    assert isinstance(data_dict, dict), f"`input` has to be of `dict` type, got {type(data_dict)}"

    result = {}

    pair_combinations = itertools.combinations(data_dict.keys(), 2)

    for item_a, item_b in pair_combinations:
        result[(item_a, item_b)] = wilcoxon(
            x=data_dict[item_a],
            y=data_dict[item_b],
            alternative=alternative,
        )

    return result


def wilcoxon_ind(data_dict, alternative="two-sided"):
    """Wilcoxon rank-sum test - Non-parametric independent test
    
    AKA Mann-Whitney U test (MWU), Mann-Whitney-Wilcoxon (MWW), 
    Wilcoxon rank-sum test, Wilcoxon-Mann-Whitney test
    
    """
    assert isinstance(data_dict, dict), f"`input` has to be of `dict` type, got {type(data_dict)}"

    result = {}

    pair_combinations = itertools.combinations(data_dict.keys(), 2)

    for item_a, item_b in pair_combinations:
        result[(item_a, item_b)] = ranksums(
            x=data_dict[item_a],
            y=data_dict[item_b],
            alternative=alternative,
        )

    return result


from scipy.stats import f_oneway


def anova_test(data_list, left_width=25, right_width=20):

    # Check have 2 or more sets
    if len(data_list) < 2:
        return

    # Check all sets have more than 1 elements
    for data in data_list:
        if len(data) < 2:
            return

    anova_stats = f_oneway(*data_list)
    pvalue = anova_stats.pvalue

    if pvalue <= 0.001:
        star = "***"
    elif pvalue <= 0.01:
        star = "**"
    elif pvalue <= 0.05:
        star = "*"
    else:
        star = ""

    result_str = "ANOVA pvalue".ljust(left_width, ".") + f"{round(pvalue, 5)} {star}".rjust(right_width, ".")

    return result_str


def get_stat_test_string(data_dict, stat_test_func, left_width=25, right_width=20) -> str:
    result_dict = stat_test_func(data_dict=data_dict)
    print_dict = {}

    for key, value in result_dict.items():
        pvalue = value.pvalue

        if pvalue <= 0.001:
            star = "***"
        elif pvalue <= 0.01:
            star = "**"
        elif pvalue <= 0.05:
            star = "*"
        else:
            star = ""

        print_dict[key] = f"{round(pvalue, 5)} {star}"

    # return "\n".join([f"{key} pvalue:    {value}" for key, value in print_dict.items()])
    return "\n".join(
        [
            f"{key} {stat_test_func.__name__} pvalue".ljust(left_width, ".") + f"{value}".rjust(right_width, ".")
            for key, value in print_dict.items()
        ]
    )
