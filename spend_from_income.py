# -----------------------------
# Calibrated Version 2A model
# Inputs: income (post-tax), age_group, gender
# Output: expected annual gambling spend
# -----------------------------

#THIS SHIT IS ALL IN POUNDS, ADJUST FOR US ACCORDINGLY SNADSXNCVDSFBNERWSNVESADJF
import scipy.stats as stats
def y1_raw(income: float) -> float:
    # Male discrete buckets (% of total spend)
    # Closest to 14144
    if income < 21216:
        return 18.0
    # Closest to 28288
    elif income < 36244:
        return 15.0
    # Closest to 44200
    elif income < 54782:
        return 16.0
    # Closest to 65364
    elif income < 94848:
        return 15.0
    # Closest to 124332
    else:
        return 10.0

def y2_raw(income: float) -> float:
    # Female discrete buckets (% of total spend)
    # Closest to 14144
    if income < 21216:
        return 7.0
    # Closest to 28288
    elif income < 36244:
        return 8.0
    # Closest to 44200
    elif income < 54782:
        return 4.0
    # Closest to 65364
    elif income < 94848:
        return 5.0
    # Closest to 124332
    else:
        return 5.0

# ---- Calibration targets from the regression table
TARGET_MALE_25_44 = 5.76
TARGET_FEMALE_25_44 = 5.76 - 4.10  # = 1.66

# ---- Reference income (median British post-tax income)
I_REF = 37874.0

# ---- Calibration multipliers (constants)
K_MALE = TARGET_MALE_25_44 / y1_raw(I_REF)
K_FEMALE = TARGET_FEMALE_25_44 / y2_raw(I_REF)

def gambling_share_percent_calibrated(income: float, gender: str) -> float:
    """
    Calibrated gambling spend share (% of total spend).
    Ensures at I_REF: male 25–44 -> 5.76%, female 25–44 -> 1.66%.
    """
    g = gender.strip().lower()
    if g == "male":
        return y1_raw(income) * K_MALE
    elif g == "female":
        return y2_raw(income) * K_FEMALE
    else:
        raise ValueError("gender must be 'male' or 'female'")


# -----------------------------
# Income → quintile mapping
# IMPORTANT: Replace thresholds with your spreadsheet's actual quintile cutoffs
# -----------------------------
def income_to_quintile(income: float) -> int:
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


# -----------------------------
# Base probability of gambling by (gender, income quintile)
# Any gambling activity, last 12 months
# -----------------------------
P_BASE = {
    "male":   {1: 0.51592466, 2: 0.50916265, 3: 0.55316983, 4: 0.62263690, 5: 0.60853887},
    "female": {1: 0.39659307, 2: 0.46383624, 3: 0.44749898, 4: 0.49886290, 5: 0.43930923},
}

# -----------------------------
# Age multiplier relative to 25–44 reference
# (proxy mapping you’re using)
# -----------------------------
AGE_MULTIPLIER = {
    "18-34": 0.7332265834,
    "35-49": 1.0,
    "50-64": 1.1017884478,
    "65+":   0.9228134479,
}

def probability_of_gambling(income: float, age_group: str, gender: str) -> float:
    g = gender.strip().lower()
    a = age_group.strip()

    if g not in P_BASE:
        raise ValueError("gender must be 'male' or 'female'")
    if a not in AGE_MULTIPLIER:
        raise ValueError("age_group must be one of: '18-24', '25-44', '45-64', '65+'")

    q = income_to_quintile(income)
    base_p = P_BASE[g][q]
    p = base_p * AGE_MULTIPLIER[a]

    # Clamp to [0, 1]
    return max(0.0, min(1.0, p))


def expected_annual_gambling_spend(income: float, age_group: str, gender: str) -> float:
    """
    Version 2A:
    expected spend = income * (calibrated share fraction) * P(gambles)
    """
    share_percent = gambling_share_percent_calibrated(income, gender)
    share_fraction = share_percent / 100.0
    p_gamble = probability_of_gambling(income, age_group, gender)
    return income * share_fraction * p_gamble

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
    p_x_greater_than_0 = even_population(age_group, gender)
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
def even_population(age_group, gender):
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
    probability_of_winning = even_population(age_group, gender)
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
# -----------------------------
if __name__ == "__main__":
    # Should print ~5.76 and ~1.66
    print("Male calibrated share at I_REF (%):", gambling_share_percent_calibrated(I_REF, "male"))
    print("Female calibrated share at I_REF (%):", gambling_share_percent_calibrated(I_REF, "female"))





# Example 1: Male, 35-49, Income 40000
income1 = 40000.0
age_group1 = "35-49"
gender1 = "male"
winners_gains1, losers_losses1 = calculate_gambling_outcomes(income1, age_group1, gender1)
print(f"For Income: {income1}, Age Group: {age_group1}, Gender: {gender1}:")
print(f"  Total Money Gained by Winners: {winners_gains1:.2f}")
print(f"  Total Money Lost by Losers: {losers_losses1:.2f}")