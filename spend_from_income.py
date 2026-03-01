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
# Age share quadratic (y is a PERCENT)
# y(age) = -0.00238169 x^2 + 0.188714 x + 0.618878
# -----------------------------
def age_share_percent(age: float) -> float:
   x = float(age)  # ensures you can pass 26 or "26"
   return -0.00238169 * x**2 + 0.188714 * x + 0.618878




# -----------------------------
# Income buckets (midpoints) on POST-TAX income
# cutoffs: 21216, 36244, 54782, 94848
# bucket 1 = lowest, bucket 5 = highest
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
# FINAL: input pretax, age (number), gender
# output = posttax_income * (age_share_percent/100) * multiplier
# -----------------------------
def expected_annual_gambling_spend(pretax_income: float, age: float, gender: str) -> float:
   posttax = calculate_uk_posttax_income(pretax_income)


   y_percent = age_share_percent(age)      # percent
   y_frac = y_percent / 100.0              # fraction


   mult = gender_income_multiplier(posttax, gender)


   return posttax * y_frac * mult




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

def calculate_gambling_outcomes(income: float, age: int, age_group: str, gender: str) -> tuple[float, float]:
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
    total_expected_annual_gambling_spend = expected_annual_gambling_spend(income, age, gender)

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
age = 36
gender1 = "male"
winners_gains1, losers_losses1 = calculate_gambling_outcomes(income1, age, age_group1, gender1)
amount_spent = expected_annual_gambling_spend(income1, age, gender1)
amount_lost = 0.09 * amount_spent
print(f"For Income: {income1}, Age Group: {age_group1}, Gender: {gender1}:")
print(f"  Total Money Gained by Winners: {winners_gains1:.2f}", "Percent winners :", win_population(age_group1, gender1))
print(f"  Total Money Lost by Losers: {losers_losses1:.2f}", "Percent losers: ", 1 - win_population(age_group1, gender1))
print(f"  Total Amount Spent on Gambling: {amount_spent:.2f}")
print(f" Total Amount Lost: {amount_lost:.2f}")
