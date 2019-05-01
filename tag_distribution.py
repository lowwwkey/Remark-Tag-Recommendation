#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
@File       : tag_distribute.py
@Discription: 备注标签推荐第一版，根据历史分布
@Author     : Guangkai Li
@Date:      : 2018/09/01
'''

import pandas as pd
import numpy as np
df = pd.read_csv('/opt/test/liguangkai/label_match/label_match_0801_0910.csv', low_memory=False)

import io
import operator
import sys
import time
from collections import defaultdict


class LabelMatch(object):
    def __init__(self, df, head = 'amaptag_thrid'):
        self.df_user = df[df['user_labels'].notnull()]
        self.df_car = df[df['labels'].notnull()]
        self.df = df
        self.head = head
    
    def attr_label_num_dict(self, user_or_car):
        df_ = self.df[(self.df[user_or_car].notnull()) & (self.df[self.head].notnull())]
        labels = list(df_[user_or_car])
        attr = list(df_[self.head])
        
        attr_label_num_dict = defaultdict(dict)
        
        for i in xrange(len(df_)):
            for l in labels[i].strip().split(','):
                if '轴' not in l:
                    attr_label_num_dict[attr[i]][l] = attr_label_num_dict[attr[i]].get(l, 0) + 1    

        return attr_label_num_dict
    
    def weighted_pro(self):
        user_attr_label_num_dict = self.attr_label_num_dict('user_labels')
        car_attr_label_num_dict = self.attr_label_num_dict('labels')
        
        pro_dict = {}
        
        for attr in car_attr_label_num_dict.keys():
            weighted_pro_dict = {}
            if attr in user_attr_label_num_dict:
                car_label_num_dict = car_attr_label_num_dict[attr]
                user_label_num_dict = user_attr_label_num_dict[attr]
                
                car_num_sum = float(np.sum(car_label_num_dict.values()))
                user_num_sum = float(np.sum(user_label_num_dict.values()))
                
                for l in set(car_label_num_dict.keys()) | set(user_label_num_dict.keys()):
                    weighted_pro_dict[l] = 0.5*car_label_num_dict.get(l, 0)/car_num_sum + 0.5*user_label_num_dict.get(l ,0)/user_num_sum

            else:
                car_label_num_dict = car_attr_label_num_dict[attr]
                car_num_sum = float(np.sum(car_label_num_dict.values()))
                
                for l in car_label_num_dict:
                    weighted_pro_dict[l] = car_label_num_dict[l]/car_num_sum
            
            sort_weighted_pro = sorted(weighted_pro_dict.items(), key=operator.itemgetter(1), reverse = True)[:10]
            
            pro_dict[attr] = sort_weighted_pro
            
        return pro_dict
   

def run(head, file_name):          
    with io.open('/opt/test/liguangkai/label_match/%s.txt'%file_name, 'w', encoding='utf-8') as f:
        
        city_list = df['city_id'].value_counts().index.tolist()

        city_list_2000 = [city for city in city_list if len(df[df['city_id']==city][df[df['city_id']==city]['customer_service_remark'].notnull()]) >= 1500]
        print('备注大于1500的城市有%s个,为：'%len(city_list_2000))
        print city_list_2000
        with io.open('/opt/test/liguangkai/label_match/label_match_city.txt', 'w', encoding='utf-8') as f_city:
            for city in city_list_2000:
                f_city.write('%s\n'%str(city).decode("utf-8"))
        
        print '开始写入文件...'
        start = time.time()
        print('---------共%s个城市----------'% len(city_list_2000))
        count = 1
        for city in city_list_2000:
            time_start = time.time()
            df_city = df[df['city_id']==city]
                
            print('准备写入第%s城市 %s' % (count, city))
            car_list = df_city['car_type'].value_counts().index.tolist()
            print('---------共%s个车型----------'% len(car_list))
            count_car = 1
            for car in car_list:
                df_car = df_city[df_city['car_type']==car]
                
                if len(df_car[df_car['car_type'].notnull()])<=10:
                    count_car += 1
                    continue
                
                d_dic = LabelMatch(df_car, head).weighted_pro()
                
                for attr in d_dic:
                    for i in d_dic[attr]:
                        f.write('%s\t%s\t%s\t%s\t%s\n'% (city, car, str(attr).decode("utf-8"), str(i[0]).decode("utf-8"), '{:.9f}'.format(i[1])))                        
                count_car += 1
            print '已写入第%s城市 %s,共用时%s秒' % (count, city, time.time()-time_start)
            count += 1
        print '全部写入完毕,共用时%s' % (time.time()-start)

if __name__ == '__main__':
    _, head, file_name = sys.argv
    run(head, file_name) 
