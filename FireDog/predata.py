import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


##准备数据

#日k线改月k线
logic={'open':'first','high':'max','low':'min',
       'close':'last','volume':'sum','ret':'sum'}
#使用akshare获取创业版指数
sz399006 = ak.stock_zh_index_daily_em(symbol="sz399006")
sz399006['ret']=sz399006['close'].pct_change()
sz399006['date']=pd.to_datetime(sz399006['date'])
sz399006 = sz399006.set_index('date')

#日K线改为月K线
m_399006 = sz399006.resample('ME').apply(logic)

#使用akshare 获取沪深300价格
sh000300 = ak.stock_zh_index_daily_em(symbol="sh000300")

#计算每月的收益率，新增ret列
sh000300['ret'] = sh000300['close'].pct_change()
sh000300['date'] = pd.to_datetime(sh000300['date'])
sh000300 = sh000300.set_index('date')

#将日线改为月K线
m_000300 = sh000300.resample('ME').apply(logic)


#合并数据，是他们在同一个列表中计算，并且对齐起始时间
ret = pd.merge(
    m_000300.reset_index()[['date','ret']],
    m_399006.reset_index()[['date','ret']],
    on='date',
    suffixes=('_sh300','_sz399006')
    )

#设置合并后的列名
ret.columns = ['date', 'm_000300', 'm_399006']
print("ret:\n {}", ret.head(20))

##计算前6个月的累计收益率
cumret = (ret[['m_000300','m_399006']] + 1).rolling(6).apply(np.prod) - 1
print("cumret:\n{}",cumret.head(20))

#每个月在沪深300和创业版之间选出累积收益率高的
cumrank = cumret.rank(axis=1,ascending=False)
print("cumrank1:\n{}",cumrank.head(20))

##分配仓位
cumrank[cumrank<=1] = 1
cumrank[cumrank>1] = np.nan
print("cumrank2:\n {}",cumrank.head(20))


