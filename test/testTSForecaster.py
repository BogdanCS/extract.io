import sys
sys.path.insert(0, '/home/bogdan/dev/COMP30040/extract.io/src')

from tsforecaster import TSForecaster

if __name__ == "__main__":
    topic = type('testclass', (object,),
                 {'years' : {'2012-01' : 20.0, '2012-02' : 27.0, '2012-03' : 30.0, '2012-04' : 31.0, '2012-05' : 32.0,
                             '2012-06' : 26.0, '2012-07' : 29.0, '2012-07' : 30.0, '2012-08' : 25.0, '2012-09': 32.0,
                             '2012-10' : 26.0, '2012-11' : 29.0, '2012-12' : 30.0, '2013-01' : 25.0, '2013-02': 32.0,
                             '2013-03' : 26.0, '2013-04' : 29.0, '2013-04' : 30.0, '2013-05' : 25.0, '2013-06': 32.0},
                  'forecastYears' : {}})()

    forecaster = TSForecaster()
    forecaster.getForecast(topic)
    print topic.forecastYears
    
