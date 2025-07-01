import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import time
from datetime import date


## 动量，强者恒强，找强者
##  计算前6个月的累计收益率

##准备数据

#日k线改月k线
##resample so that Open is the first monday price, High and low are the month min and max and
#close is the last sunday price and volume is the sum (can be customized - pandas docs)

logic={'open':'first',
       'close':'last',
       'high':'max',
       'low':'min',
       'volume':'sum',
       'amount':'sum',
       'ret':'sum'}

#start_day="20240629" end_day="20250629"

#从今天开始，10年的历史数据
today = date.today()
da=today.replace(year=today.year -10)
start_day=da.strftime("%Y%m%d")
print(start_day)
end_day=today.strftime("%Y%m%d")
print(end_day)

#使用akshare获取创业版指数
sz399006 = ak.stock_zh_index_daily_em(symbol="sz399006",start_date=start_day,end_date=end_day)

#只用close列，pct_change()是怎么算的
sz399006['ret']=sz399006['close'].pct_change()
sz399006['date']=pd.to_datetime(sz399006['date'])
sz399006 = sz399006.set_index('date')
#to csv
sz399006.to_csv("sz399006.csv")


#日K线改为月K线
m_399006 = sz399006.resample('ME').apply(logic)
m_399006.to_csv("m_sz399006.csv")

#使用akshare 获取沪深300价格
sh000300 = ak.stock_zh_index_daily_em(symbol="sh000300",start_date=start_day,end_date=end_day)

#计算每月的收益率，新增ret列
sh000300['ret'] = sh000300['close'].pct_change()
sh000300['date'] = pd.to_datetime(sh000300['date'])
sh000300 = sh000300.set_index('date')
#to csv
sh000300.to_csv("sh000300.csv")

#将日线改为月K线
m_000300 = sh000300.resample('ME').apply(logic)
m_000300.to_csv("m_000300.csv")

#合并数据，是他们在同一个列表中计算，并且对齐起始时间
ret = pd.merge(
    m_000300.reset_index()[['date','ret']],
    m_399006.reset_index()[['date','ret']],
    on='date',
    suffixes=('_sh300','_sz399006')
    )

ret.to_csv("ret.csv")

#设置合并后的列名
ret.columns = ['date', 'm_000300', 'm_399006']
print("ret:\n {}", ret.head(20))

## 动量，强者恒强，找强者
##计算前6个月的累计收益率
cumret = (ret[['m_000300','m_399006']] + 1).rolling(6).apply(np.prod) - 1
print("cumret:\n{}",cumret.head(20))
cumret.to_csv("cumret.csv")

#每个月在沪深300和创业版之间选出累积收益率高的
cumrank = cumret.rank(axis=1,ascending=False)
print("cumrank1:\n{}",cumrank.head(20))
cumrank.to_csv("cumranksort.csv")
##分配仓位
cumrank[cumrank<=1] = 1
cumrank[cumrank>1] = np.nan
cumrank.to_csv("cumrankallocate.csv")
print("cumrank2:\n {}",cumrank.head(20))

#把日期加到数据中
result = ret[['date']].copy()
#策略收益=品种收益率*品种仓位
#由于cumrank是前6个月的累积收益率排名，
#即，第t月实际是t-1月的收益率，因此要后推一位和收益率做乘积
result[['m_000300','m_399006']] = ret[['m_000300','m_399006']] * cumrank.shift()
result.to_csv("result1.csv")

#按行对两个品种的收益求和，就获得策略收益率
result['sum'] = result[['m_000300','m_399006']].sum(axis=1,skipna=True)
result.to_csv("result2.csv")
#计算策略的累计收益
result['cumret'] = (1+result['sum']).cumprod() -1
result.to_csv("result3.csv")
print ("result: \n", result.head(20))

#画图
plt.plot(result['date'],result['cumret'],color='red')
plt.show()





