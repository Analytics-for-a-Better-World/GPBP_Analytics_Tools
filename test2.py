import pandas as pd

a = pd.DataFrame({'a': [1, 2, 3],
                  'b': [4, 5, 6]})
print(a)
temp = a.median(axis=0)[0]
b = a['a'][1]
print(temp)
