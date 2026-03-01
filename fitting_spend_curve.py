import numpy as np
from scipy.optimize import curve_fit
import warnings

# 1. Define the datasets
# x-values are the same for both tables
x_data = np.array([14144, 28288, 44200, 65364, 124332])

# y-values
y_men = np.array([18, 15, 16, 15, 10])     # Green table (y1)
y_women = np.array([7, 8, 4, 5, 5])        # Blue table (y2)

# 2. Define the logistic function
def logistic_curve(x, L, k, x0, c):
    """
    L: Curve amplitude (max - min)
    k: Steepness of the curve
    x0: x-value of the sigmoid midpoint
    c: y-axis offset (minimum asymptote)
    """
    return c + L / (1 + np.exp(-k * (x - x0)))

# 3. Helper function to fit data, calculate R^2, and print results
def fit_and_evaluate(x, y, group_name, p0_guesses):
    print(f"--- Results for {group_name} ---")
    try:
        # Fit the curve
        # maxfev increased in case it needs more iterations to converge
        popt, _ = curve_fit(logistic_curve, x, y, p0=p0_guesses, maxfev=10000)
        L, k, x0, c = popt
        
        # Calculate predicted y values
        y_fit = logistic_curve(x, *popt)
        
        # Calculate R-squared
        ss_res = np.sum((y - y_fit) ** 2)           # Residual sum of squares
        ss_tot = np.sum((y - np.mean(y)) ** 2)      # Total sum of squares
        r2 = 1 - (ss_res / ss_tot)
        
        # Output parameters
        print(f"Parameters:")
        print(f"  L (Amplitude) = {L:.4f}")
        print(f"  k (Steepness) = {k:.6f}")
        print(f"  x0 (Midpoint) = {x0:.4f}")
        print(f"  c (Offset)    = {c:.4f}")
        print(f"R-squared (R^2) = {r2:.4f}\n")
        
    except RuntimeError:
        print("Error: Optimal parameters not found. Try adjusting the initial guesses (p0).\n")

# Suppress overflow warnings that occasionally happen during curve_fit testing
warnings.filterwarnings("ignore")

# 4. Run the fitting for both groups
# Initial guesses (p0) are [L, k, x0, c]
# We estimate these based on the visual drops in your data to help the algorithm converge
guess_men = [8, -0.0001, 65000, 10]  # Drops from ~18 to ~10
guess_women = [3, -0.0001, 40000, 4] # Drops from ~7 to ~4

fit_and_evaluate(x_data, y_men, "Men (Green / y1)", guess_men)
fit_and_evaluate(x_data, y_women, "Women (Blue / y2)", guess_women)