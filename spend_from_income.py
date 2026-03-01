# -----------------------------
# Calibrated Version 2A model
# Inputs: income (post-tax), age_group, gender
# Output: expected annual gambling spend
# -----------------------------

#THIS SHIT IS ALL IN POUNDS, ADJUST FOR US ACCORDINGLY SNADSXNCVDSFBNERWSNVESADJF

import scipy.stats as stats

# -----------------------------
# Calibrated Version 2A model
# Inputs: income (post-tax), age_group, gender
# Output: expected annual gambling spend
# -----------------------------


import scipy.stats as stats




def calculate_uk_posttax_income(pretax_income: float) -> float:
    if pretax_income < 0:
        raise ValueError("pretax_income must be non-negative")


    income = float(pretax_income)


    # Personal allowance: 12,570, tapered by £1 for every £2 above £100,000.
    if income <= 100_000:
        personal_allowance = 12_570.0
    else:
        reduction = (income - 100_000.0) / 2.0
        personal_allowance = max(0.0, 12_570.0 - reduction)


    taxable_income = max(0.0, income - personal_allowance)


    # Progressive tax on taxable income:
    basic_band = 37_700.0
    higher_band = 74_870.0


    basic_tax = min(taxable_income, basic_band) * 0.20
    higher_tax = min(max(taxable_income - basic_band, 0.0), higher_band) * 0.40
    additional_tax = max(taxable_income - basic_band - higher_band, 0.0) * 0.45


    total_tax = basic_tax + higher_tax + additional_tax
    return income - total_tax




# -----------------------------
# Age share quadratic (returns a PERCENT)
# y(age) = -0.00238169 x^2 + 0.188714 x + 0.618878
# -----------------------------
def age_share_percent(age: float) -> float:
    x = float(age)
    return -0.00238169 * x**2 + 0.188714 * x + 0.618878




# -----------------------------
# Income buckets on POST-TAX income
# cutoffs: 21216, 36244, 54782, 94848
# -----------------------------
def income_to_bucket(posttax_income: float) -> int:
    income = float(posttax_income)
    if income < 21216:
        return 1
    elif income < 36244:
        return 2
    elif income < 54782:
        return 3
    elif income < 94848:
        return 4
    else:
        return 5


# Compatibility alias: old code calls it "quintile"
def income_to_quintile(income: float) -> int:
    return income_to_bucket(income)




# -----------------------------
# Bucket rates (PERCENT) from your table
# Ordered LOWEST -> HIGHEST bucket
# Men:    [10, 15, 16, 15, 18]
# Women:  [5,  5,  4,  8,  7]
# Baseline man = male in bucket 3 => 16%
# -----------------------------
MEN_RATE_BY_BUCKET   = {1: 10.0, 2: 15.0, 3: 16.0, 4: 15.0, 5: 18.0}
WOMEN_RATE_BY_BUCKET = {1: 5.0,  2: 5.0,  3: 4.0,  4: 8.0,  5: 7.0}
BASELINE_MALE_RATE = 16.0




def gender_income_multiplier(posttax_income: float, gender: str) -> float:
    g = gender.strip().lower()
    b = income_to_bucket(posttax_income)


    if g == "male":
        rate = MEN_RATE_BY_BUCKET[b]
    elif g == "female":
        rate = WOMEN_RATE_BY_BUCKET[b]
    else:
        raise ValueError("gender must be 'male' or 'female'")


    return rate / BASELINE_MALE_RATE




# -----------------------------
# Block-1 compatibility: y1_raw / y2_raw + calibration constants
# Block 1's gambling_share_percent_calibrated() expects:
#   y1_raw(income), y2_raw(income), K_MALE, K_FEMALE, I_REF
# -----------------------------
def y1_raw(income: float) -> float:
    """Male bucket rate (PERCENT). Used by block 1 calibration."""
    b = income_to_bucket(income)
    return MEN_RATE_BY_BUCKET[b]


def y2_raw(income: float) -> float:
    """Female bucket rate (PERCENT). Used by block 1 calibration."""
    b = income_to_bucket(income)
    return WOMEN_RATE_BY_BUCKET[b]


# ---- Calibration targets from your regression table (same as old block 2)
TARGET_MALE_25_44 = 5.76
TARGET_FEMALE_25_44 = 1.66  # (= 5.76 - 4.10)


# ---- Reference income (keep your old reference post-tax income value)
I_REF = 37874.0


# ---- Calibration multipliers
# (If you don't WANT calibration anymore, set K_MALE = K_FEMALE = 1.0 instead.)
K_MALE = TARGET_MALE_25_44 / y1_raw(I_REF)
K_FEMALE = TARGET_FEMALE_25_44 / y2_raw(I_REF)




# -----------------------------
# Age-group -> representative age
# Block 1 uses age_group strings like: "18-34", "35-49", "50-64", "65+"
# -----------------------------
AGE_GROUP_TO_REP_AGE = {
    "18-24": 21.0,   # optional support
    "25-44": 34.5,   # optional support
    "45-64": 54.5,   # optional support
    "18-34": 26.0,
    "35-49": 42.0,
    "50-64": 57.0,
    "65+":   70.0,
    "75+":   80.0,   # optional support
}


def _rep_age_from_group(age_group: str) -> float:
    a = age_group.strip()
    if a not in AGE_GROUP_TO_REP_AGE:
        raise ValueError(
            "age_group must be one of: "
            + ", ".join(sorted(AGE_GROUP_TO_REP_AGE.keys()))
        )
    return AGE_GROUP_TO_REP_AGE[a]




# -----------------------------
# FINAL (block-1 compatible signature):
# input: income (POST-tax), age_group (string), gender
# output: expected annual gambling spend
#
# Uses your block-3 model:
#   spend = posttax_income * (age_share_percent(rep_age)/100) * gender_income_multiplier(posttax, gender)
# -----------------------------
def expected_annual_gambling_spend(income: float, age_group: str, gender: str) -> float:
    posttax = float(income)
    rep_age = _rep_age_from_group(age_group)


    y_percent = age_share_percent(rep_age)          # percent
    mult = gender_income_multiplier(posttax, gender)  # unitless


    share_percent = y_percent * mult                # percent
    return posttax * (share_percent / 100.0)




# def gambling_share_percent_calibrated(income: float, gender: str) -> float:
#     """
#     Calibrated gambling spend share (% of total spend).
#     Ensures at I_REF: male 25–44 -> 5.76%, female 25–44 -> 1.66%.
#     """
#     g = gender.strip().lower()
#     if g == "male":
#         return y1_raw(income) * K_MALE
#     elif g == "female":
#         return y2_raw(income) * K_FEMALE
#     else:
#         raise ValueError("gender must be 'male' or 'female'")
    
#based on percent spending 500+ in one day
def get_risky_population(age_group, gender):
    gender_risk = 0

    if gender == "male":
        gender_risk =  0.28
    else:
        gender_risk = 0.15

    table_ages = {
            "18-24": 0.25,
    "25-44": 0.26,
    "45-64": 0.2,
    "65+":   0.03,
    }
    return 0.5 * table_ages[age_group] + 0.5 * gender_risk


def get_normal_dist_params(age_group: str, gender: str):
    """
    Calculates the mean and standard deviation of the underlying normal distribution
    based on the given age group and gender, using the 'even_population' function.
    """
    mean = -0.09
    p_x_greater_than_0 = win_population(age_group, gender)
    p_x_less_than_or_equal_0 = 1 - p_x_greater_than_0

    # Calculate the z-score corresponding to X=0
    # This z_score corresponds to X=0 in our target distribution
    z_score_at_0 = stats.norm.ppf(p_x_less_than_or_equal_0, loc=0, scale=1)

    # Calculate the standard deviation
    if z_score_at_0 == 0:
        if p_x_less_than_or_equal_0 == 0.5:
            std_dev = float('inf')
        else:
            std_dev = 1e-9
    elif abs(z_score_at_0) < 1e-9:
        std_dev = float('inf')
    else:
        std_dev = (0 - mean) / z_score_at_0

    # Standard deviation should always be non-negative
    std_dev = abs(std_dev)

    return mean, std_dev
#based on break even percent
def win_population(age_group, gender):
    gender_even = 0

    if gender == "male":
        gender_even =  0.33
    else:
        gender_even = 0.25

    table_ages = {
            "18-34": 0.33,
    "35-49": 0.29,
    "50-64": 0.17,
    "65+":   0.25,
    }
    return 0.5 * table_ages[age_group] + 0.5 * gender_even



def amount_lost(age_group: str, gender: str) -> float:
    """
    Calculates the average value (expected loss) of the normal distribution
    given that the value is less than 0 (X < 0).
    """
    mean, std_dev = get_normal_dist_params(age_group, gender)

    if std_dev == 0:
        # If std_dev is 0, all values are at the mean. If mean < 0, it's a loss.
        return min(0.0, mean)
    if std_dev == float('inf'):
        # For infinite std_dev, the distribution is flat or ill-defined in this context.
        # Return 0 as a safe default for a practical average.
        return 0.0

    # Z-score for the truncation point (0)
    z_0 = (0 - mean) / std_dev

    # Probability of X < 0
    p_x_less_than_0 = stats.norm.cdf(z_0)

    if p_x_less_than_0 == 0:
        return 0.0 # No values less than 0

    # Truncated mean formula E[X | X < a] = mu - sigma * (phi( (a-mu)/sigma ) / Phi( (a-mu)/sigma ))
    truncated_mean_loss = mean - std_dev * (stats.norm.pdf(z_0) / p_x_less_than_0)
    return truncated_mean_loss


def amount_won(age_group: str, gender: str) -> float:
    """
    Calculates the average value (expected win) of the normal distribution
    given that the value is greater than 0 (X > 0).
    """
    mean, std_dev = get_normal_dist_params(age_group, gender)

    if std_dev == 0:
        # If std_dev is 0, all values are at the mean. If mean > 0, it's a win.
        return max(0.0, mean)
    if std_dev == float('inf'):
        # Similar logic as amount_lost, return 0 for safety.
        return 0.0

    # Z-score for the truncation point (0)
    z_0 = (0 - mean) / std_dev

    # Probability of X > 0
    p_x_greater_than_0 = 1 - stats.norm.cdf(z_0)

    if p_x_greater_than_0 == 0:
        return 0.0 # No values greater than 0

    # Truncated mean formula E[X | X > a] = mu + sigma * (phi( (a-mu)/sigma ) / (1 - Phi( (a-mu)/sigma )))
    truncated_mean_win = mean + std_dev * (stats.norm.pdf(z_0) / p_x_greater_than_0)
    return truncated_mean_win

def calculate_gambling_outcomes(income: float, age_group: str, gender: str) -> tuple[float, float]:
    """
    Orchestrates the calculation of money gained by winners and money lost by losers
    based on income, age group, and gender.

    Args:
        income (float): The individual's post-tax income.
        age_group (str): The age group of the individual (e.g., '18-34', '35-49').
        gender (str): The gender of the individual ('male' or 'female').

    Returns:
        (float, float): A tuple containing (total_money_gained_by_winners, total_money_lost_by_losers).
    """
    # 1. Calculate total_expected_annual_gambling_spend
    total_expected_annual_gambling_spend = expected_annual_gambling_spend(income, age_group, gender)

    # 2. Determine probability of winning and losing
    probability_of_winning = win_population(age_group, gender)
    probability_of_losing = 1 - probability_of_winning

    # 3. Calculate average_amount_won_per_unit and average_amount_lost_per_unit
    average_amount_won_per_unit = amount_won(age_group, gender)
    average_amount_lost_per_unit = amount_lost(age_group, gender)

    # 4. Compute total money gained by winners and total money lost by losers
    total_money_gained_by_winners = total_expected_annual_gambling_spend * probability_of_winning * average_amount_won_per_unit
    # amount_lost returns a negative value, so we take its absolute value for 'money lost'
    total_money_lost_by_losers = total_expected_annual_gambling_spend * probability_of_losing * abs(average_amount_lost_per_unit)

    return total_money_gained_by_winners, total_money_lost_by_losers
# -----------------------------
# Sanity checks
# -------



# Example 1: Male, 35-49, Income 40000
income1 = 40000.0
age_group1 = "35-49"
gender1 = "male"
winners_gains1, losers_losses1 = calculate_gambling_outcomes(income1, age_group1, gender1)
print(f"For Income: {income1}, Age Group: {age_group1}, Gender: {gender1}:")
print(f"  Total Money Gained by Winners: {winners_gains1:.2f}", "Percent winners :", win_population(age_group1, gender1))
print(f"  Total Money Lost by Losers: {losers_losses1:.2f}", "Percent losers: ", 1 - win_population(age_group1, gender1))