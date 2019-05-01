# -*- coding:utf-8 -*-

'''
@File       : tag_click_num.py
@Discription: 统计点击率，及统计点击标签数量
@Author     : Guangkai Li
@Date:      : 2018/12/05
'''

import json
import numpy as np
import pandas as pd
import re
import time
from collections import Counter, defaultdict
from time import sleep
from tqdm import tqdm


def load_date():
    '''
    导入数据，计算有备注比率
    '''
    global df_label, df_remark
    df_label = pd.read_csv('./data/label_0123_0217.csv',
                           delimiter='\t', error_bad_lines=False)
    df_remark = pd.read_csv('./data/remark_0123_0217.csv',
                            delimiter='\t', error_bad_lines=False)
    remark_rate = len(
        df_remark[df_remark['customer_service_remark'].notnull()])/len(df_remark)
    print("有备注比率：%s" % remark_rate)


def other_tag_rate():
    '''
    计算其他标签的点击率
    '''
    need = ['雨布', '小推车', '拖车', '网绳', '全拆座', '半拆座', '不拆座', '加长']
    huo = ['门板', '管线', '石材', '龙骨', '家具', '腻子粉', '防盗门', '电器', '绿植', '磁砖', '易碎品']
    r = list(df_remark[df_remark['customer_service_remark'].notnull()]
             ['customer_service_remark'])
    n_total, n_need, n_huo = 0, 0, 0
    for i in r:
        m = re.split(' |,|，|!|！|、|。|;|；', str(i).strip())
        if m[0] != 'nan':
            n_total += 1
        if len(set(need) & set(m)) > 0:
            n_need += 1
        if len(set(huo) & set(m)) > 0:
            n_huo += 1
    print("原需求标签点击率：%s，货物描述标签点击率：%s" %
          (float(n_need)/n_total, float(n_huo)/n_total))


def check_rec_tag():
    with open('./data/label_match_city.txt', 'r') as f_city:
        city_list = f_city.read().strip().split('\n')

    df_l1 = df_label[(df_label['city_id'].isin(city_list))
                     & (df_label['labels'] != '-')]
    df_r1 = df_remark[df_remark['city_id'].isin(city_list)]

    biz_list = list(df_r1['user_id'])
    remark_list = list(df_r1['customer_service_remark'])

    mix_dict = defaultdict(list)
    mix_list = list(df_l1['mix'])
    for i in range(len(mix_list)):
        mix_dict[mix_list[i]].append(i)

    labels_rec = []
    N = len(df_r1)
    print('共%s条数据' % len(df_r1))
    for i in range(N):
        print("进度:{0}%".format(round((i + 1) * 100 / N)), end="\r")
        time1 = time.time()
        tmp = df_r1.iloc[[i]]
        cand = df_l1.iloc[mix_dict[tmp['mix'].values[0]]]

        d = dict(zip(cand['logtime'].values, cand['logtime'].index))

        tmp_t = tmp['create_time'].values[0]
        format_time = time.strptime(tmp_t, "%Y-%m-%d %H:%M:%S")
        timestamp = time.mktime(format_time)

        d_ = dict(zip([time.mktime(time.strptime(t, "%Y-%m-%d %H:%M:%S"))
                       for t in d.keys()], d.keys()))

        try:
            indx = sorted([(timestamp-i, i)
                           for i in d_.keys() if timestamp-i >= 0])[0][1]
            labels_rec.append(cand.loc[[d[d_[indx]]]]['labels'].values[0])
        except IndexError:
            labels_rec.append(0)

    #---------------- 标签点击率 -----------------
    m_1, n_1, m_2, n_2 = 0, 0, 0, 0
    for i in range(len(labels_rec)):
        if labels_rec[i] != 0:
            if labels_rec[i].split(',')[:3] == ['食品','电子产品','建材']:
                l = labels_rec[i].split(',')
                remark_split = re.split(' |,|，|!|！|、|。|;|；', str(remark_list[i]).strip())
                if remark_split[0]!='nan':
                    n_1 += 1
                if len(set(l)&set(remark_split)) > 0:
                    m_1 += 1
            else:
                l = labels_rec[i].split(',')
                remark_split = re.split(' |,|，|!|！|、|。|;|；', str(remark_list[i]).strip())
                if remark_split[0]!='nan':
                    n_2 += 1
                if len(set(l)&set(remark_split)) > 0:
                    m_2 += 1
    print("对照组点击率：%s，实验组点击率：%s" % (m_1/n_1, m_2/n_2))

    return labels_rec, df_r1, remark_list

def show_click_num(labels_rec, df_r1, remark_list, head='amaptag_thrid'): # start_biz_id, user_id
    feature_list = list(df_r1['%s'%head]) 
    car_list = list(df_r1['car_type'])
    city_list = list(df_r1['city_id'])

    show_click_num = {}

    for i in range(len(labels_rec)):
        if feature_list[i] is not np.nan and labels_rec[i] != 0:
            show_click_num[city_list[i]] = show_click_num.get(city_list[i], {})
            show_click_num[city_list[i]][car_list[i]] = show_click_num[city_list[i]].get(car_list[i], defaultdict(dict))
            show_click_num[city_list[i]][car_list[i]][feature_list[i]]['show'] = show_click_num[city_list[i]][car_list[i]][feature_list[i]].get('show', Counter())
            show_click_num[city_list[i]][car_list[i]][feature_list[i]]['click'] = show_click_num[city_list[i]][car_list[i]][feature_list[i]].get('click', Counter())
        
            show = labels_rec[i].strip().split(',')
            click = re.split(' |,|，|!|！|、|。|;|；', str(remark_list[i]).strip())
        
            show_click_num[city_list[i]][car_list[i]][feature_list[i]]['show'].update(show)
            show_click_num[city_list[i]][car_list[i]][feature_list[i]]['click'].update(set(click)&set(show))
    return show_click_num


def main():
    load_date()
    other_tag_rate()
    labels_rec, df_r1, remark_list = check_rec_tag()
    poi_num = show_click_num(labels_rec, df_r1, remark_list)
    biz_num = show_click_num(labels_rec, df_r1, remark_list, 'start_biz_id')
    uid_num = show_click_num(labels_rec, df_r1, remark_list, 'user_id')
    with open('./data/poi_0123_0217.json', 'w') as file:
        json.dump(poi_num, file, ensure_ascii=False)
    with open('./data/biz_0123_0217.json', 'w') as biz_f:
        json.dump(biz_num, biz_f, ensure_ascii=False)
    with open('./data/uid_0123_0217.json', 'w') as uid_f:
        json.dump(uid_num, uid_f, ensure_ascii=False)


if __name__ == "__main__":
    main()
