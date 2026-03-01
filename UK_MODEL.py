import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 1. Setting up the UK Data
ages = np.array([25, 40, 57, 70, 75])
incomes = np.array([13829, 25144, 37874, 51786, 81733])

proportions_matrix = np.array([
    [0.2197555861, 0.4875278396, 0.5752019855, 0.6669292859, 0.7104572205],
    [0.2441969774, 0.4484409800, 0.5903046945, 0.6845016027, 0.7578554562],
    [0.3382023284, 0.5096563793, 0.6179014627, 0.6661259800, 0.7345062582],
    [0.4224311230, 0.5615653834, 0.6386333633, 0.6956474723, 0.7449402322],
    [0.4893629330, 0.6262965320, 0.6956117653, 0.7155292936, 0.7750333403]
])

df = pd.DataFrame(proportions_matrix, index=ages, columns=incomes)
df.index.name = 'age'

df_long = df.reset_index().melt(
    id_vars='age',
    var_name='income',
    value_name='disposable_proportion'
)

# Extract 1D arrays of floats for SciPy
income_data = df_long['income'].values.astype(float)
age_data = df_long['age'].values.astype(float)
y_data = df_long['disposable_proportion'].values.astype(float)

# 2. Define the Non-Linear Model
# Equation: z = a * e^(b * income) + c * age^2 + d * age + f
def custom_model(X, a, b, c, d, f):
    inc, ag = X # Unpack the X variables
    return a * np.exp(b * inc) + c * (ag**2) + d * ag + f

# 3. Fit the Model
# We need to provide an initial guess (p0) for the optimizer.
# For exponential decay, we guess 'a' is negative and 'b' is a tiny negative number.
initial_guess = [-0.5, -0.00005, 0.0001, 0.01, 0.5]

# popt contains the optimized parameters [a, b, c, d, f]
popt, pcov = curve_fit(
    custom_model, 
    (income_data, age_data), # X variables passed as a tuple
    y_data, 
    p0=initial_guess, 
    maxfev=10000 # Give it enough iterations to converge
)

print(f"Optimized Parameters:")
print(f"  a (exp scale): {popt[0]:.4e}")
print(f"  b (exp decay rate): {popt[1]:.4e}")
print(f"  c (age^2 coef): {popt[2]:.4e}")
print(f"  d (age coef): {popt[3]:.4e}")
print(f"  f (constant): {popt[4]:.4f}")

# 4. 3D Plotting Function (Adapted for SciPy popt)
def plot_3d_nonlinear_regression(age_data, income_data, y_data, popt):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create the smooth grid
    age_grid = np.linspace(age_data.min(), age_data.max(), 50)
    tax_grid = np.linspace(income_data.min(), income_data.max(), 50)
    age_mesh, tax_mesh = np.meshgrid(age_grid, tax_grid)
    
    # Calculate Z using the custom model and optimized parameters
    # *popt unrolls the list into the a, b, c, d, f arguments
    Z = custom_model((tax_mesh, age_mesh), *popt)
    
    # Plotting
    ax.plot_surface(age_mesh, tax_mesh, Z, alpha=0.6, cmap='viridis')
    ax.scatter(age_data, income_data, y_data, color='red', s=50, label='Actual UK Data', depthshade=False)
    
    # Labels
    ax.set_xlabel('Age')
    ax.set_ylabel('Income')
    ax.set_zlabel('Disposable Proportion')
    ax.set_title('Income vs. Age vs. Disposable Proportion')
    plt.legend()
    plt.show()

# 5. Run the plot!
plot_3d_nonlinear_regression(age_data, income_data, y_data, popt)