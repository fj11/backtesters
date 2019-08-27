
import talib
    
class Tec():

    def __init__(self, data):
        self.__data = data
        return
    
    def ACOS(self, name, **parameters):
        data = self.__data[name]
        return talib.ACOS(data, **parameters)
    
    def AD(self, name, **parameters):
        data = self.__data[name]
        return talib.AD(data, **parameters)
    
    def ADD(self, name, **parameters):
        data = self.__data[name]
        return talib.ADD(data, **parameters)
    
    def ADOSC(self, name, **parameters):
        data = self.__data[name]
        return talib.ADOSC(data, **parameters)
    
    def ADX(self, name, **parameters):
        data = self.__data[name]
        return talib.ADX(data, **parameters)
    
    def ADXR(self, name, **parameters):
        data = self.__data[name]
        return talib.ADXR(data, **parameters)
    
    def APO(self, name, **parameters):
        data = self.__data[name]
        return talib.APO(data, **parameters)
    
    def AROON(self, name, **parameters):
        data = self.__data[name]
        return talib.AROON(data, **parameters)
    
    def AROONOSC(self, name, **parameters):
        data = self.__data[name]
        return talib.AROONOSC(data, **parameters)
    
    def ASIN(self, name, **parameters):
        data = self.__data[name]
        return talib.ASIN(data, **parameters)
    
    def ATAN(self, name, **parameters):
        data = self.__data[name]
        return talib.ATAN(data, **parameters)
    
    def ATR(self, name, **parameters):
        data = self.__data[name]
        return talib.ATR(data, **parameters)
    
    def AVGPRICE(self, name, **parameters):
        data = self.__data[name]
        return talib.AVGPRICE(data, **parameters)
    
    def BBANDS(self, name, **parameters):
        data = self.__data[name]
        return talib.BBANDS(data, **parameters)
    
    def BETA(self, name, **parameters):
        data = self.__data[name]
        return talib.BETA(data, **parameters)
    
    def BOP(self, name, **parameters):
        data = self.__data[name]
        return talib.BOP(data, **parameters)
    
    def CCI(self, name, **parameters):
        data = self.__data[name]
        return talib.CCI(data, **parameters)
    
    def CDL2CROWS(self, name, **parameters):
        data = self.__data[name]
        return talib.CDL2CROWS(data, **parameters)
    
    def CDL3BLACKCROWS(self, name, **parameters):
        data = self.__data[name]
        return talib.CDL3BLACKCROWS(data, **parameters)
    
    def CDL3INSIDE(self, name, **parameters):
        data = self.__data[name]
        return talib.CDL3INSIDE(data, **parameters)
    
    def CDL3LINESTRIKE(self, name, **parameters):
        data = self.__data[name]
        return talib.CDL3LINESTRIKE(data, **parameters)
    
    def CDL3OUTSIDE(self, name, **parameters):
        data = self.__data[name]
        return talib.CDL3OUTSIDE(data, **parameters)
    
    def CDL3STARSINSOUTH(self, name, **parameters):
        data = self.__data[name]
        return talib.CDL3STARSINSOUTH(data, **parameters)
    
    def CDL3WHITESOLDIERS(self, name, **parameters):
        data = self.__data[name]
        return talib.CDL3WHITESOLDIERS(data, **parameters)
    
    def CDLABANDONEDBABY(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLABANDONEDBABY(data, **parameters)
    
    def CDLADVANCEBLOCK(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLADVANCEBLOCK(data, **parameters)
    
    def CDLBELTHOLD(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLBELTHOLD(data, **parameters)
    
    def CDLBREAKAWAY(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLBREAKAWAY(data, **parameters)
    
    def CDLCLOSINGMARUBOZU(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLCLOSINGMARUBOZU(data, **parameters)
    
    def CDLCONCEALBABYSWALL(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLCONCEALBABYSWALL(data, **parameters)
    
    def CDLCOUNTERATTACK(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLCOUNTERATTACK(data, **parameters)
    
    def CDLDARKCLOUDCOVER(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLDARKCLOUDCOVER(data, **parameters)
    
    def CDLDOJI(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLDOJI(data, **parameters)
    
    def CDLDOJISTAR(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLDOJISTAR(data, **parameters)
    
    def CDLDRAGONFLYDOJI(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLDRAGONFLYDOJI(data, **parameters)
    
    def CDLENGULFING(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLENGULFING(data, **parameters)
    
    def CDLEVENINGDOJISTAR(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLEVENINGDOJISTAR(data, **parameters)
    
    def CDLEVENINGSTAR(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLEVENINGSTAR(data, **parameters)
    
    def CDLGAPSIDESIDEWHITE(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLGAPSIDESIDEWHITE(data, **parameters)
    
    def CDLGRAVESTONEDOJI(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLGRAVESTONEDOJI(data, **parameters)
    
    def CDLHAMMER(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLHAMMER(data, **parameters)
    
    def CDLHANGINGMAN(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLHANGINGMAN(data, **parameters)
    
    def CDLHARAMI(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLHARAMI(data, **parameters)
    
    def CDLHARAMICROSS(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLHARAMICROSS(data, **parameters)
    
    def CDLHIGHWAVE(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLHIGHWAVE(data, **parameters)
    
    def CDLHIKKAKE(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLHIKKAKE(data, **parameters)
    
    def CDLHIKKAKEMOD(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLHIKKAKEMOD(data, **parameters)
    
    def CDLHOMINGPIGEON(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLHOMINGPIGEON(data, **parameters)
    
    def CDLIDENTICAL3CROWS(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLIDENTICAL3CROWS(data, **parameters)
    
    def CDLINNECK(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLINNECK(data, **parameters)
    
    def CDLINVERTEDHAMMER(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLINVERTEDHAMMER(data, **parameters)
    
    def CDLKICKING(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLKICKING(data, **parameters)
    
    def CDLKICKINGBYLENGTH(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLKICKINGBYLENGTH(data, **parameters)
    
    def CDLLADDERBOTTOM(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLLADDERBOTTOM(data, **parameters)
    
    def CDLLONGLEGGEDDOJI(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLLONGLEGGEDDOJI(data, **parameters)
    
    def CDLLONGLINE(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLLONGLINE(data, **parameters)
    
    def CDLMARUBOZU(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLMARUBOZU(data, **parameters)
    
    def CDLMATCHINGLOW(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLMATCHINGLOW(data, **parameters)
    
    def CDLMATHOLD(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLMATHOLD(data, **parameters)
    
    def CDLMORNINGDOJISTAR(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLMORNINGDOJISTAR(data, **parameters)
    
    def CDLMORNINGSTAR(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLMORNINGSTAR(data, **parameters)
    
    def CDLONNECK(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLONNECK(data, **parameters)
    
    def CDLPIERCING(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLPIERCING(data, **parameters)
    
    def CDLRICKSHAWMAN(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLRICKSHAWMAN(data, **parameters)
    
    def CDLRISEFALL3METHODS(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLRISEFALL3METHODS(data, **parameters)
    
    def CDLSEPARATINGLINES(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLSEPARATINGLINES(data, **parameters)
    
    def CDLSHOOTINGSTAR(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLSHOOTINGSTAR(data, **parameters)
    
    def CDLSHORTLINE(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLSHORTLINE(data, **parameters)
    
    def CDLSPINNINGTOP(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLSPINNINGTOP(data, **parameters)
    
    def CDLSTALLEDPATTERN(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLSTALLEDPATTERN(data, **parameters)
    
    def CDLSTICKSANDWICH(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLSTICKSANDWICH(data, **parameters)
    
    def CDLTAKURI(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLTAKURI(data, **parameters)
    
    def CDLTASUKIGAP(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLTASUKIGAP(data, **parameters)
    
    def CDLTHRUSTING(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLTHRUSTING(data, **parameters)
    
    def CDLTRISTAR(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLTRISTAR(data, **parameters)
    
    def CDLUNIQUE3RIVER(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLUNIQUE3RIVER(data, **parameters)
    
    def CDLUPSIDEGAP2CROWS(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLUPSIDEGAP2CROWS(data, **parameters)
    
    def CDLXSIDEGAP3METHODS(self, name, **parameters):
        data = self.__data[name]
        return talib.CDLXSIDEGAP3METHODS(data, **parameters)
    
    def CEIL(self, name, **parameters):
        data = self.__data[name]
        return talib.CEIL(data, **parameters)
    
    def CMO(self, name, **parameters):
        data = self.__data[name]
        return talib.CMO(data, **parameters)
    
    def CORREL(self, name, **parameters):
        data = self.__data[name]
        return talib.CORREL(data, **parameters)
    
    def COS(self, name, **parameters):
        data = self.__data[name]
        return talib.COS(data, **parameters)
    
    def COSH(self, name, **parameters):
        data = self.__data[name]
        return talib.COSH(data, **parameters)
    
    def DEMA(self, name, **parameters):
        data = self.__data[name]
        return talib.DEMA(data, **parameters)
    
    def DIV(self, name, **parameters):
        data = self.__data[name]
        return talib.DIV(data, **parameters)
    
    def DX(self, name, **parameters):
        data = self.__data[name]
        return talib.DX(data, **parameters)
    
    def EMA(self, name, **parameters):
        data = self.__data[name]
        return talib.EMA(data, **parameters)
    
    def EXP(self, name, **parameters):
        data = self.__data[name]
        return talib.EXP(data, **parameters)
    
    def FLOOR(self, name, **parameters):
        data = self.__data[name]
        return talib.FLOOR(data, **parameters)
    
    def HT_DCPERIOD(self, name, **parameters):
        data = self.__data[name]
        return talib.HT_DCPERIOD(data, **parameters)
    
    def HT_DCPHASE(self, name, **parameters):
        data = self.__data[name]
        return talib.HT_DCPHASE(data, **parameters)
    
    def HT_PHASOR(self, name, **parameters):
        data = self.__data[name]
        return talib.HT_PHASOR(data, **parameters)
    
    def HT_SINE(self, name, **parameters):
        data = self.__data[name]
        return talib.HT_SINE(data, **parameters)
    
    def HT_TRENDLINE(self, name, **parameters):
        data = self.__data[name]
        return talib.HT_TRENDLINE(data, **parameters)
    
    def HT_TRENDMODE(self, name, **parameters):
        data = self.__data[name]
        return talib.HT_TRENDMODE(data, **parameters)
    
    def KAMA(self, name, **parameters):
        data = self.__data[name]
        return talib.KAMA(data, **parameters)
    
    def LINEARREG(self, name, **parameters):
        data = self.__data[name]
        return talib.LINEARREG(data, **parameters)
    
    def LINEARREG_ANGLE(self, name, **parameters):
        data = self.__data[name]
        return talib.LINEARREG_ANGLE(data, **parameters)
    
    def LINEARREG_INTERCEPT(self, name, **parameters):
        data = self.__data[name]
        return talib.LINEARREG_INTERCEPT(data, **parameters)
    
    def LINEARREG_SLOPE(self, name, **parameters):
        data = self.__data[name]
        return talib.LINEARREG_SLOPE(data, **parameters)
    
    def LN(self, name, **parameters):
        data = self.__data[name]
        return talib.LN(data, **parameters)
    
    def LOG10(self, name, **parameters):
        data = self.__data[name]
        return talib.LOG10(data, **parameters)
    
    def MA(self, name, **parameters):
        data = self.__data[name]
        return talib.MA(data, **parameters)
    
    def MACD(self, name, **parameters):
        data = self.__data[name]
        return talib.MACD(data, **parameters)
    
    def MACDEXT(self, name, **parameters):
        data = self.__data[name]
        return talib.MACDEXT(data, **parameters)
    
    def MACDFIX(self, name, **parameters):
        data = self.__data[name]
        return talib.MACDFIX(data, **parameters)
    
    def MAMA(self, name, **parameters):
        data = self.__data[name]
        return talib.MAMA(data, **parameters)
    
    def MAVP(self, name, **parameters):
        data = self.__data[name]
        return talib.MAVP(data, **parameters)
    
    def MAX(self, name, **parameters):
        data = self.__data[name]
        return talib.MAX(data, **parameters)
    
    def MAXINDEX(self, name, **parameters):
        data = self.__data[name]
        return talib.MAXINDEX(data, **parameters)
    
    def MEDPRICE(self, name, **parameters):
        data = self.__data[name]
        return talib.MEDPRICE(data, **parameters)
    
    def MFI(self, name, **parameters):
        data = self.__data[name]
        return talib.MFI(data, **parameters)
    
    def MIDPOINT(self, name, **parameters):
        data = self.__data[name]
        return talib.MIDPOINT(data, **parameters)
    
    def MIDPRICE(self, name, **parameters):
        data = self.__data[name]
        return talib.MIDPRICE(data, **parameters)
    
    def MIN(self, name, **parameters):
        data = self.__data[name]
        return talib.MIN(data, **parameters)
    
    def MININDEX(self, name, **parameters):
        data = self.__data[name]
        return talib.MININDEX(data, **parameters)
    
    def MINMAX(self, name, **parameters):
        data = self.__data[name]
        return talib.MINMAX(data, **parameters)
    
    def MINMAXINDEX(self, name, **parameters):
        data = self.__data[name]
        return talib.MINMAXINDEX(data, **parameters)
    
    def MINUS_DI(self, name, **parameters):
        data = self.__data[name]
        return talib.MINUS_DI(data, **parameters)
    
    def MINUS_DM(self, name, **parameters):
        data = self.__data[name]
        return talib.MINUS_DM(data, **parameters)
    
    def MOM(self, name, **parameters):
        data = self.__data[name]
        return talib.MOM(data, **parameters)
    
    def MULT(self, name, **parameters):
        data = self.__data[name]
        return talib.MULT(data, **parameters)
    
    def NATR(self, name, **parameters):
        data = self.__data[name]
        return talib.NATR(data, **parameters)
    
    def OBV(self, name, **parameters):
        data = self.__data[name]
        return talib.OBV(data, **parameters)
    
    def PLUS_DI(self, name, **parameters):
        data = self.__data[name]
        return talib.PLUS_DI(data, **parameters)
    
    def PLUS_DM(self, name, **parameters):
        data = self.__data[name]
        return talib.PLUS_DM(data, **parameters)
    
    def PPO(self, name, **parameters):
        data = self.__data[name]
        return talib.PPO(data, **parameters)
    
    def ROC(self, name, **parameters):
        data = self.__data[name]
        return talib.ROC(data, **parameters)
    
    def ROCP(self, name, **parameters):
        data = self.__data[name]
        return talib.ROCP(data, **parameters)
    
    def ROCR(self, name, **parameters):
        data = self.__data[name]
        return talib.ROCR(data, **parameters)
    
    def ROCR100(self, name, **parameters):
        data = self.__data[name]
        return talib.ROCR100(data, **parameters)
    
    def RSI(self, name, **parameters):
        data = self.__data[name]
        return talib.RSI(data, **parameters)
    
    def SAR(self, name, **parameters):
        data = self.__data[name]
        return talib.SAR(data, **parameters)
    
    def SAREXT(self, name, **parameters):
        data = self.__data[name]
        return talib.SAREXT(data, **parameters)
    
    def SIN(self, name, **parameters):
        data = self.__data[name]
        return talib.SIN(data, **parameters)
    
    def SINH(self, name, **parameters):
        data = self.__data[name]
        return talib.SINH(data, **parameters)
    
    def SMA(self, name, **parameters):
        data = self.__data[name]
        return talib.SMA(data, **parameters)
    
    def SQRT(self, name, **parameters):
        data = self.__data[name]
        return talib.SQRT(data, **parameters)
    
    def STDDEV(self, name, **parameters):
        data = self.__data[name]
        return talib.STDDEV(data, **parameters)
    
    def STOCH(self, name, **parameters):
        data = self.__data[name]
        return talib.STOCH(data, **parameters)
    
    def STOCHF(self, name, **parameters):
        data = self.__data[name]
        return talib.STOCHF(data, **parameters)
    
    def STOCHRSI(self, name, **parameters):
        data = self.__data[name]
        return talib.STOCHRSI(data, **parameters)
    
    def SUB(self, name, **parameters):
        data = self.__data[name]
        return talib.SUB(data, **parameters)
    
    def SUM(self, name, **parameters):
        data = self.__data[name]
        return talib.SUM(data, **parameters)
    
    def T3(self, name, **parameters):
        data = self.__data[name]
        return talib.T3(data, **parameters)
    
    def TAN(self, name, **parameters):
        data = self.__data[name]
        return talib.TAN(data, **parameters)
    
    def TANH(self, name, **parameters):
        data = self.__data[name]
        return talib.TANH(data, **parameters)
    
    def TEMA(self, name, **parameters):
        data = self.__data[name]
        return talib.TEMA(data, **parameters)
    
    def TRANGE(self, name, **parameters):
        data = self.__data[name]
        return talib.TRANGE(data, **parameters)
    
    def TRIMA(self, name, **parameters):
        data = self.__data[name]
        return talib.TRIMA(data, **parameters)
    
    def TRIX(self, name, **parameters):
        data = self.__data[name]
        return talib.TRIX(data, **parameters)
    
    def TSF(self, name, **parameters):
        data = self.__data[name]
        return talib.TSF(data, **parameters)
    
    def TYPPRICE(self, name, **parameters):
        data = self.__data[name]
        return talib.TYPPRICE(data, **parameters)
    
    def ULTOSC(self, name, **parameters):
        data = self.__data[name]
        return talib.ULTOSC(data, **parameters)
    
    def VAR(self, name, **parameters):
        data = self.__data[name]
        return talib.VAR(data, **parameters)
    
    def WCLPRICE(self, name, **parameters):
        data = self.__data[name]
        return talib.WCLPRICE(data, **parameters)
    
    def WILLR(self, name, **parameters):
        data = self.__data[name]
        return talib.WILLR(data, **parameters)
    
    def WMA(self, name, **parameters):
        data = self.__data[name]
        return talib.WMA(data, **parameters)
    