import numpy as np
import matplotlib.pyplot as plt

#ANOTHER POSSIBILITY: graph neccessary income vs age and then subtract that flat amount from inputted after tax income
after_tax = np.array([39089.66,	76376.54,	93247.69,	101475.56,	88944.01,	58507.06, 	44807.81])
disposable_income = np.array([-4041.35,	5505.54, 5262.69, 9119.56 ,9024.01,	-3888.94 ,-8800.19])
age = np.array([(25+18)/2, (34+25)/2, (44+35)/2, (54+45)/2, (64+55)/2, (74+65)/2, (78+75)/2]) #averaging age brackets, maybe make better lattr

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
    plt.scatter(after_tax, disposable_income/after_tax)
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

#use UK data to confirm linear and quadratic relationships
X = np.stack([age ** 2, age, after_tax, np.ones_like(age)]).transpose()
w = np.linalg.pinv(X) @ proportion
print(w)
plot_3d_regression(age, after_tax, proportion, w)

