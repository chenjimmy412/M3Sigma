import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#ANOTHER POSSIBILITY: graph neccessary income vs age and then subtract that flat amount from inputted after tax income

#change US numbers and do UK

#--legacy info
after_tax_not_including_married = np.array([39089.66,	76376.54,	93247.69,	101475.56,	88944.01,	58507.06, 	44807.81]) 
disposable_income_not_including_married = np.array([-4041.35,	5505.54, 5262.69, 9119.56 ,9024.01,	-3888.94 ,-8800.19])



#assuming everyone above 29.5 is married and everyone below is single 
age = np.array([(25+18)/2, (34+25)/2, (44+35)/2, (54+45)/2, (64+55)/2, (74+65)/2, (78+75)/2]) #averaging age brackets, maybe make better lattr
after_tax = np.array([ 39047.66,	 82254.94,	101881.89,	110383.18,	96772.53,	66360.58,	50368.04 ])
disposable_income = np.array([991.65,	22947.94,	28563.89,	34201.18,	30047.53,	9360.58, -597.96])
# plt.title("Age vs disposable income")
# plt.scatter(age, disposable_income)
# plt.show()


proportion = disposable_income/after_tax

def age_prop_reg():
    plt.title("Age vs Proportion of after tax income (state) that is disposable")
    plt.scatter(age, disposable_income/after_tax)
    #plt.show()

    #interperet age vs proportion disposable income as quartic?? to model mid-life dip due to children entering the house but then leaving house


    X = np.stack([age ** 2, age, np.ones_like(age)]).transpose()
    print(X)

    w = np.linalg.pinv(X) @ proportion
    print(w)

    plt.plot(age, X @ w)
    plt.show()

def show_income_vs_proportion():
    plt.title("Income vs Proportion of after tax income (state) that is disposable")
    X = np.stack([after_tax, np.ones_like(after_tax)]).transpose()
    w = np.linalg.pinv(X) @ proportion
    plt.scatter(after_tax, disposable_income/after_tax)
    print("INCOME VS DISP PROP WEIGHTs", w)
    plt.plot(after_tax, X @ w)
    plt.show()

#CHEF MIKED PLOTRTING FUNC
def plot_3d_regression(age, after_tax, proportion, w):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. Create a grid of values to draw the smooth surface
    age_grid = np.linspace(age.min(), age.max(), 50)
    tax_grid = np.linspace(after_tax.min(), after_tax.max(), 50)
    age_mesh, tax_mesh = np.meshgrid(age_grid, tax_grid)
    
    # 2. Calculate the predicted proportion (Z) for every point on the grid
    # w[0] = age^2, w[1] = age, w[2] = after_tax, w[3] = constant
    Z = w[0] * age_mesh**2 + w[1] * age_mesh + w[2] * tax_mesh + w[3]
    
    # 3. Plot the predicted surface and the actual data points
    ax.plot_surface(age_mesh, tax_mesh, Z, alpha=0.6, cmap='viridis')
    ax.scatter(age, after_tax, proportion, color='red', s=50, label='Actual Data', depthshade=False)
    
    # 4. Labels and display
    ax.set_xlabel('Age')
    ax.set_ylabel('After Tax Income')
    ax.set_zlabel('Disposable Proportion')
    ax.set_title('3D Regression: Age & Income vs Disposable Proportion')
    plt.legend()
    plt.show()


#--- switching over to EXPONENTIAL relationship between income and disp instead of linear

def show_income_vs_proportion_exp():
    plt.title("Income vs Proportion of after tax income (state) that is disposable")
    
    # Define the 1D exponential decay model
    def exp_model(x, a, b, c):
        return a * np.exp(b * x) + c
    
    # Provide an initial guess [a, b, c] so the optimizer doesn't get lost
    p0 = [-1.0, -0.00005, 0.5]
    popt, _ = curve_fit(exp_model, after_tax, proportion, p0=p0, maxfev=10000)
    
    print("INCOME VS DISP PROP EXP WEIGHTS (a, b, c):", popt)
    
    # Plot original scatter
    plt.scatter(after_tax, proportion, label="Actual Data")
    
    # Plot smooth exponential curve
    tax_sorted = np.linspace(after_tax.min(), after_tax.max(), 100)
    plt.plot(tax_sorted, exp_model(tax_sorted, *popt), color='red', label="Exp Fit")
    
    plt.legend()
    plt.show()

def linear_income_quad_age_reg(): #legacy
    print("--- Running Original Linear(Income) / Quad(Age) 3D Regression ---")
    
    X = np.stack([age ** 2, age, after_tax, np.ones_like(age)]).transpose()
    w = np.linalg.pinv(X) @ proportion
    
    print("Linear/Quad 3D Weights:", w)
    
    plot_3d_regression(age, after_tax, proportion, w)

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

age = np.array([(25+18)/2, (34+25)/2, (44+35)/2, (54+45)/2, (64+55)/2, (74+65)/2, (78+75)/2])
after_tax = np.array([39047.66, 82254.94, 101881.89, 110383.18, 96772.53, 66360.58, 50368.04])
disposable_income = np.array([991.65, 22947.94, 28563.89, 34201.18, 30047.53, 9360.58, -597.96])
proportion = disposable_income / after_tax

def exp_income_quad_age_reg():
    print("--- Running New Exp(Income) / Quad(Age) 3D Regression ---")
    
    # Define the 3D model
    def exp_quad_model(X_data, a, b, c, d, f):
        tax_val, age_val = X_data
        return a * np.exp(b * tax_val) + c * (age_val**2) + d * age_val + f

    p0 = [-0.5, -0.00001, 0.0001, 0.01, 0.5]
    popt, _ = curve_fit(exp_quad_model, (after_tax, age), proportion, p0=p0, maxfev=10000)
    
    print("Exp/Quad 3D Weights (a, b, c, d, f):", popt)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    age_grid = np.linspace(age.min(), age.max(), 50)
    tax_grid = np.linspace(after_tax.min(), after_tax.max(), 50)
    age_mesh, tax_mesh = np.meshgrid(age_grid, tax_grid)
    
    Z = exp_quad_model((tax_mesh, age_mesh), *popt)
    
    ax.plot_surface(age_mesh, tax_mesh, Z, alpha=0.6, cmap='viridis')
    ax.scatter(age, after_tax, proportion, color='red', s=50, label='Actual Data', depthshade=False)
    
    ax.set_xlabel('Age')
    ax.set_ylabel('After Tax Income')
    ax.set_zlabel('Disposable Proportion')
    ax.set_title('Age vs. Income vs Disposable Proportion')
    plt.legend()
    plt.show()

def exp_quad_model(X_data, a, b, c, d, f):
    tax_val, age_val = X_data
    return a * np.exp(b * tax_val) + c * (age_val**2) + d * age_val + f

p0 = [-0.5, -0.00001, 0.0001, 0.01, 0.5]
popt, _ = curve_fit(exp_quad_model, (after_tax, age), proportion, p0=p0, maxfev=10000)

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

age_grid = np.linspace(age.min(), age.max(), 50)
tax_grid = np.linspace(after_tax.min(), after_tax.max(), 50)
age_mesh, tax_mesh = np.meshgrid(age_grid, tax_grid)

Z = exp_quad_model((tax_mesh, age_mesh), *popt)

ax.plot_surface(age_mesh, tax_mesh, Z, alpha=0.6, cmap='viridis')
ax.scatter(age, after_tax, proportion, color='red', s=50, label='Actual US Data', depthshade=False)

ax.set_xlabel('Age', labelpad=8)
ax.xaxis.label.set_rotation(-10)  # rotate Age label to match axis angle
ax.set_ylabel('After Tax Income', labelpad=15)
ax.set_zlabel('Disposable Proportion')
ax.set_title('Age vs. Income vs Disposable Proportion', pad=5)  # reduced pad to bring title closer

# Flip the age axis so it reads low-to-high left-to-right (aligned with axis direction)
ax.invert_xaxis()

plt.legend()
plt.tight_layout()
print("Saved.")

exp_income_quad_age_reg()



