import numpy as np

def predict_disposable(age, after_tax_income):
    w = np.array([-3.69382117e-04, 3.45537414e-02, -6.50702748e-01])
    return np.polyval(w, age) * after_tax_income

def predict_disposable_3D(age, after_tax_income):
    w = np.array([-1.82934802e-04,   #age **2
                    1.63719299e-02 , #age
                    1.97255115e-06,  #income
                    -4.33800040e-01], #bias
                    )
    
    return (
        w[0] * age**2 +
        w[1] * age +
        w[2] * after_tax_income +
        w[3]
    ) * after_tax_income


#TODO: UPDATE THIS TO EXP
def predict_disposable_incomeonly(age, after_tax_income):
    w = np.array([ 3.87536698e-06, -2.90776265e-01])
    return (
        w[0] * after_tax_income +
        w[1]
    ) * after_tax_income


def predict_disposable_3D_exp(country, age, after_tax_income):
    if country == "US":
        return (-1.21372866e+00 * np.exp(-4.13915766e-05 * after_tax_income) - 1.65247314e-04 * (age**2) + 1.42036735e-02 * age + 3.18330510e-02) * after_tax_income
    if country == "UK":
        return (-8.0218e-01 * np.exp(-4.8440e-05 * (after_tax_income/1.34)) + 5.9501e-05 * (age**2) - 3.6455e-03 * age + 0.7602) * (after_tax_income/1.34)
    return None

age, after_tax_income = (35, 120_000)
print("OUR MODEL: \n", "UK: ", predict_disposable_3D_exp("UK", age, after_tax_income), "\nUS: ", predict_disposable_3D_exp("US", age, after_tax_income) )
print("age only: ", predict_disposable(age, after_tax_income), "age and income: ", predict_disposable_3D(age, after_tax_income), "income only: ", predict_disposable_incomeonly(age, after_tax_income))