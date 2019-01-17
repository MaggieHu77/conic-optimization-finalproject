#!/usr/bin/python
# coding:utf-8

import tushare as ts
import numpy as np
from constant import *
import pandas as pd


# 获取数据调用接口


# 随机从指定市场指数成分股当中选择若干股票代码
# 喵了个咪权限不足，tusare太黑心
# def get_codes(pro, num, mkt, date):
#     df = pro.index_weight(index_code=mkt, start_date=date, end_date=date)["con_code"]
#     codes = df.values
#     np.random.shuffle(codes)
#     codes = codes[0:num]
#     return list(codes)


def get_codes(num):
    df = ts.get_sz50s()["code"]
    codes = df.values
    np.random.shuffle(codes)
    codes = codes[0:num]
    codes = [cc+".SZ" if cc[0] == '0' else cc+".SH" for cc in codes]
    return list(codes)


# 获取一只股票指定区间内的日收益率
def get_return(pro, code, start_date, end_date):
    df = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)[["pct_chg", "trade_date"]]
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
    df.rename(columns={"pct_chg": code}, inplace=True)
    df.set_index("trade_date", inplace=True)
    return df


# 获取所有样本股票数据，并组合为table
def get_all_returns(pro, codes, start_date, end_date):
    df = None
    for cc in codes:
        dfc = get_return(pro=pro, code=cc, start_date=start_date, end_date=end_date)
        if df.__class__ is not dfc.__class__:
            df = dfc
        else:
            df = pd.concat([df, dfc], join="outer", axis=1)
    return df


if __name__ == "__main__":
    pro = ts.pro_api("7a7a28e59757d5f8ed48cf7254f2185340f2b528e334ff888a394948")
    # unit test
    codes = get_codes(num=N)
    print(codes)
    # unit test
    # df1 = get_return(pro, codes[0], START_DATE, END_DATE)
    # print(df1.head(5))
    # unit test
    df2 = get_all_returns(pro, codes[0:2], START_DATE, END_DATE)
    print(df2.head(2))