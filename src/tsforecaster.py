import pandas as pd
import numpy as np
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.stattools import adfuller
import matplotlib.pylab as plt
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 15, 6
from matplotlib import pyplot

# We may need a bigger range of the data - or more granular - consider months?
# Store months and use it for forecasting but remove them before sending to UI? (i.e when expanding)

class TSForecaster(object):
    FUTURE_TIME_WINDOW = 5 # years

    # Maybe use this for evaluation?
    # copied from analytics vidhya
    def testStationarity(self, timeseries):
        #Determing rolling statistics
        rolmean = pd.rolling_mean(timeseries, window=3)
        rolstd = pd.rolling_std(timeseries, window=3)

        #Plot rolling statistics:
        #orig = plt.plot(timeseries, color='blue',label='Original')
        #mean = plt.plot(rolmean, color='red', label='Rolling Mean')
        #std = plt.plot(rolstd, color='black', label = 'Rolling Std')
        #plt.legend(loc='best')
        #plt.title('Rolling Mean & Standard Deviation')
        #plt.show(block=False)
        
        #Perform Dickey-Fuller test:
        print 'Results of Dickey-Fuller Test:'
        dftest = adfuller(timeseries, autolag='AIC')
        dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
        for key,value in dftest[4].items():
            dfoutput['Critical Value (%s)'%key] = value
        print dfoutput

    def convertToPD(self, yearCounts):
        pd = {'date' : [],
              'docs' : []}
        for year, count in yearCounts.iteritems():
            pd['date'].append(year + '-01')
            pd['docs'].append(count)
        return pd
        
    def createDataframe(self, data):
        df = pd.DataFrame(data, columns = ['date', 'docs'])
        df['date'] = pd.to_datetime(df['date'])
        df.index = df['date']
        del df['date']
        df.sort_index(axis=0, inplace=True)
        return df

    def getForecast(self, topic):
        # Create time series dataframe
        df = self.createDataframe(self.convertToPD(topic.years))
        ts = df['docs']
      # tsLog = np.log(ts)
      # http://machinelearningmastery.com/arima-for-time-series-forecasting-with-python/
      # do the testing training to find the best p,q,d parameters for the model
        history = [val for val in ts.values]
        predictions = list()
        for t in range(0,10):
            model = ARIMA(history, order=(3,1,0))
            model_fit = model.fit(disp=-1)
            output = model_fit.forecast()
            print output[0]
            yhat = output[0]
            predictions.append(yhat)
            history.append(yhat)
        pyplot.plot(predictions)
        pyplot.show(block=False)
        
      #  # Remove trends/seasonality
      #  tsLog = np.log(ts)
      #  #tsLog = ts
      #  # First order differencing
      #  tsLogDiff = tsLog - tsLog.shift()
      #  tsLogDiff.dropna(inplace=True)
      #  self.testStationarity(tsLogDiff)
      #  
      #  # Create forecasting model
      #  # The mid parameter 1 means that first order differencing will be taken
      #  # 0,1,2 ; 3, 1, 0 
      #  model = ARIMA(tsLog, order=(3, 1, 0))  
      #  results_ARIMA = model.fit(disp=-1)   
      #  
      #  # Convert values back to original scale
      #  # Auto Regressive model
      #  # Can be improved by combining it with Moving Averages
      #  predictions_ARIMA_diff = pd.Series(results_ARIMA.fittedvalues, copy=True)
      #  #predictions_ARIMA_diff = pd.Series(results_ARIMA.forecast(steps=1), copy=True)
      #  #predictions_ARIMA_diff = pd.Series(results_ARIMA.predict(start='2012-02', end='2014-12', typ='levels'), copy=True)
      #  print predictions_ARIMA_diff.head()
      #  predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()
      #  print predictions_ARIMA_diff_cumsum.head()
      #  print tsLog.ix[0]
      #  #tsLog.index.append(pd.Index(['2013-07-01']))
      #  #idx = pd.date_range('2013-07-01', '2014-12-01', freq='M')
      #  #tsLog = ts.reindex(idx, fill_value=0)
      #  #print tsLog.index
      #  predictions_ARIMA_log = pd.Series(tsLog.ix[0], index=tsLog.index)
      #  predictions_ARIMA_log = predictions_ARIMA_log.add(predictions_ARIMA_diff_cumsum,fill_value=0)
      #  predictions_ARIMA_log.head()
      #  predictions_ARIMA = np.exp(predictions_ARIMA_log)
      #  plt.plot(ts)
      #  plt.plot(predictions_ARIMA)
      #  plt.show(block=False)
      #  plt.title('RMSE: %.4f'% np.sqrt(sum((predictions_ARIMA-ts)**2)/len(ts)))
        
        topic.forecastYears = []

        while(True):
            x=1
