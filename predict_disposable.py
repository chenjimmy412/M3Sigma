import numpy as np

def predict_disposable(age, after_tax_income):
    w = np.array([-3.31572789e-04,  3.06891944e-02, -5.94578935e-01])
    return np.polyval(w, age) * after_tax_income

def predict_disposable_3D(age, after_tax_income):
    w = np.array([-2.27956499e-04  2.06236661e-02  1.33949904e-06 -4.83538861e-01])


print(predict_disposable(19, 100_000))