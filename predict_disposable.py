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

def predict_disposable_incomeonly(age, after_tax_income):
    w = np.array([ 3.87536698e-06, -2.90776265e-01])
    return (
        w[0] * after_tax_income +
        w[1]
    ) * after_tax_income

print(predict_disposable(23, 120_000), predict_disposable_3D(23, 120_000), predict_disposable_incomeonly(23, 120_000))