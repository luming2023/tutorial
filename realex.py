import akshare as ak

#real time?

stock_zh_a_spot_df = ak.stock_zh_a_spot_em()
stock_zh_a_spot_df.to_csv("real_a.csv")
print(stock_zh_a_spot_df[stock_zh_a_spot_df['代码'] == '600919'])
