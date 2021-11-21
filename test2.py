import pandas as pd
import numpy as np
import math
from datetime import datetime

a = pd.DataFrame({'a': [1, 2, 3],
                  'b': [4, 5, 6]})
print(a)
temp = a.median(axis=0)[0]
b = a['a'][1]
print(temp)

a = [[1, 2], [3, 4], [5, 6]]
print(pd.DataFrame(a))

a = [np.nan, np.nan]
print(math.isnan(max(a)))
print(datetime.today())
