import pandas as pd
import xml.etree.ElementTree as ET
file_path = "export.xml"
df = pd.read_xml(file_path)

df=df.drop([
	'HKCharacteristicTypeIdentifierDateOfBirth', 'HKCharacteristicTypeIdentifierBiologicalSex', 
	'HKCharacteristicTypeIdentifierBloodType', 
	'HKCharacteristicTypeIdentifierFitzpatrickSkinType', 
	'HKCharacteristicTypeIdentifierCardioFitnessMedicationsUse', 
	'sourceName', 'sourceVersion','startDate', 'endDate', 'device', 'unit'
], axis=1)

df = df[df['type'] == 'HKQuantityTypeIdentifierStepCount']
df=df.drop(['type'], axis=1)
df['value'] = df['value'].astype(int)
df['creationDate'] = pd.to_datetime(df['creationDate'])
df['creationDate'] = df['creationDate'].dt.date
df = df.groupby('creationDate').sum().reset_index() 

df['value_lag'] = df['value'].shift(1)

for window in [3, 7]:
    df[f'rolling_mean_{window}'] = df['value_lag'].rolling(window=window).mean()
    df[f'rolling_std_{window}'] = df['value_lag'].rolling(window=window).std()
    df[f'rolling_min_{window}'] = df['value_lag'].rolling(window=window).min()
    df[f'rolling_max_{window}'] = df['value_lag'].rolling(window=window).max()

df = df.dropna()

cols = ['value_lag', 'rolling_mean_3', 'rolling_std_3',
       'rolling_min_3', 'rolling_max_3', 'rolling_mean_7', 'rolling_std_7',
       'rolling_min_7', 'rolling_max_7']

for col in cols:
    df[col]=df[col].astype(int)

print(type(df['creationDate']))
df['creationDate'] = pd.to_datetime(df['creationDate'])
df['day'] = df['creationDate'].dt.dayofweek
df['month'] = df['creationDate'].dt.month

df["day_te"]=(
   df.groupby('day')['value']
   .transform(lambda x: x.shift().expanding().mean())
)


df["month_te"]=(
   df.groupby('month')['value']
   .transform(lambda x: x.shift().expanding().mean())
)

df = df.drop(['creationDate'],axis=1)
df = df.dropna()
cols = ['value','value_lag','rolling_mean_3','rolling_std_3','rolling_min_3',
        'rolling_max_3','rolling_mean_7','rolling_std_7','rolling_min_7','rolling_max_7','day','month','day_te','month_te' ]

for col in cols:
    df[col] = df[col].astype(int)


#print(df.head(20))
#print(df.columns.tolist)

from sklearn.model_selection import TimeSeriesSplit
X=df.drop(columns=['value'])
y=df['value']

tscv=TimeSeriesSplit(n_splits=3)

for train_index, val_index in tscv.split(X):
    X_train, X_val=X.iloc[train_index], X.iloc[val_index]
    y_train, y_val=y.iloc[train_index], y.iloc[val_index]

import xgboost as xgb
model=xgb.XGBRegressor()
model.fit(X_train, y_train)

y_pred = model.predict(X_val)

from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
mae=mean_absolute_error(y_val,y_pred)
rmse=np.sqrt(mean_squared_error(y_val,y_pred))

print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")


initial_train_size = 100
forecast_horizon = 1 

predictions = []
true_values = []

for i in range(initial_train_size, len(df) - forecast_horizon):
    train = df.iloc[:i]
    test = df.iloc[i:i + forecast_horizon]

    X_train = train.drop(columns='value')
    y_train = train['value']

    X_test = test.drop(columns='value')
    y_test = test['value']

    model = xgb.XGBRegressor()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    predictions.append(y_pred[0])
    true_values.append(y_test.values[0])

# Evaluate
roll_mae = mean_absolute_error(true_values, predictions)

print(f"Rolling Forecast MAE: {roll_mae:.2f}")

