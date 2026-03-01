# -----------------------------
# Calibrated Version 2A model
# Inputs: income (post-tax), age_group, gender
# Output: expected annual gambling spend
# -----------------------------

#THIS SHIT IS ALL IN POUNDS, ADJUST FOR US ACCORDINGLY SNADSXNCVDSFBNERWSNVESADJF

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
    "18-24": 0.7332265834,
    "25-44": 1.0,
    "45-64": 1.1017884478,
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


# -----------------------------
# Sanity checks
# -----------------------------
if __name__ == "__main__":
    # Should print ~5.76 and ~1.66
    print("Male calibrated share at I_REF (%):", gambling_share_percent_calibrated(I_REF, "male"))
    print("Female calibrated share at I_REF (%):", gambling_share_percent_calibrated(I_REF, "female"))

    # Example
    print("Expected annual gambling spend:",
          expected_annual_gambling_spend(40000, "25-44", "male"))




print(expected_annual_gambling_spend(38000,"25-44","male"))

#money lost
print(expected_annual_gambling_spend(38000,"65+","female") * (0.09 - get_risky_population("65+","female") * 0.37) )
