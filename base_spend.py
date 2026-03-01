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

print(expected_annual_gambling_spend(100000, 20, "female"))