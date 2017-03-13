import pandas as pd
import math
import numpy as np
from dateutil import relativedelta as rd
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.stattools import adfuller
#import matplotlib.pylab as plt
#from matplotlib.pylab import rcParams
#rcParams['figure.figsize'] = 15, 6
#from matplotlib import pyplot

# We may need a bigger range of the data - or more granular - consider months?
# Store months and use it for forecasting but remove them before sending to UI? (i.e when expanding)

class TSForecaster(object):
    FUTURE_TIME_WINDOW = 5 # years
    FIND_BEST_PARAMS = True
    DEFAULT_P = 0
    DEFAULT_D = 0
    DEFAULT_Q = 0

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
        print data
        df = pd.DataFrame(data, columns = ['date', 'docs'])
        df['date'] = pd.to_datetime(df['date'])
        df.index = df['date']
        del df['date']
        df.sort_index(axis=0, inplace=True)
        return df

    def getArimaForecast(self, history, p, d, q):
        model = ARIMA(history, order=(p,d,q))
        model_fit = model.fit(disp=-1)
        output = model_fit.forecast()
        return output[0]

    def getForecast(self, topic):
        # Create time series dataframe
        df = self.createDataframe(self.convertToPD(topic.years))
        ts = df['docs']
        
        # Fill missing data by linear interpolation
        print ts
        ts = ts.reindex(pd.date_range(min(df.index), max(df.index), freq='MS'))
        ts = ts.interpolate()
        print ts
                   
      # tsLog = np.log(ts)
        history = []
        bestp = TSForecaster.DEFAULT_P
        bestd = TSForecaster.DEFAULT_D
        bestq = TSForecaster.DEFAULT_Q
        # Find best parameters for model
        if (TSForecaster.FIND_BEST_PARAMS == True):
            # Split time series into training and evaluation set
            X = ts.values
            size = int(len(X) * 0.66)
            train, evl = X[0:size], X[size:len(X)]
            history = [val for val in train]
            predictions = list()
            min_error = 1000000
            for p in range(0,2):
                for d in range(1,3):
                    for q in range(2,4):
                        try:
                            for t in range(len(evl)):
                                forecast = self.getArimaForecast(history, p, d, q)
                                observ = evl[t] 
                                predictions.append(forecast)
                                history.append(observ)
                            error = mean_squared_error(evl, predictions)
                            print('Test MSE: %.3f' % error)
                            if (error < min_error):
                                min_error = error
                                bestp = p
                                bestq = q
                                bestd = d
                                #pyplot.plot(predictions)
                                #pyplot.plot(evl)
                                #pyplot.show(block=False)
                        except:
                            print "Continue"
                                
        else:
            history = [val for val in ts.values]

            
        print "ARIMA parameters: %d, %d, %d" % (bestp, bestd, bestq)
        # Make predictions
        baseDate = max(df.index)
        # try catch try again with 0 0 0
        try:
            for t in range(0, TSForecaster.FUTURE_TIME_WINDOW*12):
                forecast = self.getArimaForecast(history, bestp, bestd ,bestq)
                date = baseDate + rd.relativedelta(years=int(math.floor(t/12)), months=t%12)
                topic.forecastYears[str(date.year) + "-" + str(date.month)] = int(math.floor(forecast))
                history.append(forecast)
        except:
            for t in range(0, TSForecaster.FUTURE_TIME_WINDOW*12):
                forecast = self.getArimaForecast(history, 0, 0 ,0)
                date = baseDate + rd.relativedelta(years=int(math.floor(t/12)), months=t%12)
                topic.forecastYears[str(date.year) + "-" + str(date.month)] = int(math.floor(forecast))
                history.append(forecast)
            

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
