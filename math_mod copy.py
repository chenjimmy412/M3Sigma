import numpy as np
import matplotlib.pyplot as plt

after_tax_single = np.array([39089.66,	76376.54,	93247.69,	101475.56,	88944.01,	58507.06, 	44807.81])
disposable_income_single = np.array([-4041.35,	5505.54, 5262.69, 9119.56 ,9024.01,	-3888.94 ,-8800.19])
age = np.array([(25+18)/2, (34+25)/2, (44+35)/2, (54+45)/2, (64+55)/2, (74+65)/2, (78+75)/2]) #averaging age brackets, maybe make better lattr

# plt.title("Age vs disposable income")
# plt.scatter(age, disposable_income)
# plt.show()

proportion = disposable_income/after_tax
plt.title("Age vs Proportion of after tax income (state) that is disposable")
plt.scatter(age, disposable_income/after_tax)
#plt.show()

#interperet age vs proportion disposable income as quartic to model mid-life dip due to children entering the house but then leaving house



