
import numpy as np
import matplotlib.pyplot as plt

# Shared x values
x = np.array([25, 40, 57, 70, 75]) #averaging the age brackets to get points

# Quintile data
data = {
    "Bottom quintile": np.array([0.2197555861, 0.2441969774, 0.3382023284, 0.422431123, 0.489362933]),
    "Second quintile": np.array([0.4875278396, 0.44844098, 0.5096563793, 0.5615653834, 0.626296532]),
    "Third quintile": np.array([0.5752019855, 0.5903046945, 0.6179014627, 0.6386333633, 0.6956117653]),
    "Fourth quintile": np.array([0.6669292859, 0.6845016027, 0.66612598, 0.6956474723, 0.7155292936]),
    "Fifth quintile": np.array([0.7104572205, 0.7578554562, 0.7345062582, 0.7449402322, 0.7750333403]),
}

# Smooth x grid for plotting fits
x_fit = np.linspace(x.min(), x.max(), 300)

plt.figure()

for label, y in data.items():
    # Quadratic regression
    coeffs = np.polyfit(x, y, 2)
    poly = np.poly1d(coeffs)

    # Plot data and fit
    plt.scatter(x, y, label=label)
    plt.plot(x_fit, poly(x_fit), label=f"{label} fit")

plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.show()
