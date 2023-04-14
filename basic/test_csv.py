import csv
import numpy as np
import pandas as pd

df = pd.read_csv('F_PRED_MAINT_TMP_1.csv', nrows=200)
print(df.head())