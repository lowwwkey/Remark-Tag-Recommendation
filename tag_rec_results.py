# -*- coding: utf-8 -*-

'''
@File       : tag_click_num.py
@Discription: 根据历史点击数据，由UCB算法优化标签
@Author     : Guangkai Li
@Date:      : 2018/12/08
'''

import json
import numpy as np
from collections import Counter, defaultdict


def load_json(head = 'poi'): # uid, biz
    global num_1, num_2
    with open("./data/%s_merge_0930_0121.json"%head, "r") as f_old:
        num_1 = json.load(f_old)
    with open("./data/%s_0123_0217.json"%head, "r") as f_part:
        num_2 = json.load(f_part)

def merge_data(head):
    for city in num_1:
        for car in num_1[city]:
            if city in num_2.keys() and car in num_2[city].keys():
                new_num = list(set(num_2[city][car].keys()) -
                           set(num_1[city][car].keys()))
                if len(new_num) > 0:
                    for head in new_num:
                        num_1[city][car][head] = num_2[city][car][head]
                for head in num_1[city][car]:
                    if head in num_2[city][car]:
                        num_1[city][car][head]['show'] = Counter(
                            num_1[city][car][head]['show'])+Counter(num_2[city][car][head]['show'])
                        num_1[city][car][head]['click'] = Counter(
                            num_1[city][car][head]['click'])+Counter(num_2[city][car][head]['click'])

    with open("./data/%s_merge_0930_0217.json" % head, "w") as f:
        json.dump(num_1, f, ensure_ascii=False)

    show_click_num = num_1

    return show_click_num

# -------------------- UCB ---------------------- 
MAX_BERNOULLI_RANDOM_VARIABLE_VARIANCE = 0.25


def get_ucb_dict(d):
    '''
	由UCB算法得到每个标签的预期点击收益
	
	Args:
		d: {tag1:{"show":num1,"click":num2}, tag2:{...}, ...}
		
	Returns:
		由预期收益对标签排序后的结果
    '''
    ucb_dict = defaultdict(dict)
    for feature in d:
        t = float(np.sum(np.array(list(d[feature]['show'].values()))))
        for label in d[feature]['show']:
            totals = d[feature]['show'][label]
            successes = d[feature]['click'].get(label, 0)
            estimated_means = successes/totals if totals > 0 else 0  # sample mean
            estimated_variances = estimated_means - \
                estimated_means**2 if totals > 0 else MAX_BERNOULLI_RANDOM_VARIABLE_VARIANCE
            UCB = estimated_means + 1.96*np.sqrt(estimated_variances/totals)
            ucb_dict[feature][label] = UCB
    for feature in ucb_dict:
        ucb_dict[feature] = sorted(
            ucb_dict[feature].items(), key=lambda item: item[1], reverse=True)
    return ucb_dict

def write_file(head, show_click_num):
    lab_rec = defaultdict(dict)
    for city in show_click_num:
        for car in show_click_num[city]:
            lab_rec[city][car] = get_ucb_dict(show_click_num[city][car])

    filter_list = ['门板', '管线', '石材', '龙骨', '家具',
               '腻子粉', '防盗门', '电器', '绿植', '磁砖', '易碎品']

    car1_label = ['全拆座', '半拆座', '不拆座', '高顶', '平顶', '加长']
    car5_label = ['高顶', '平顶', '加长']
    car0_label = ['全拆座', '半拆座', '不拆座']

    with open('./data/%s标签推荐.txt'%head, 'w', encoding='utf-8') as f:
        for city in lab_rec:
            for car in lab_rec[city]:
                for feature in lab_rec[city][car]:
                    if int(car) == 1:
                        for label in car1_label:
                            f.write('%s\t%s\t%s\t%s\t%s\n' % (str(city), str(
                                car), str(feature), str(label), str(1000.0)))
                        for t in lab_rec[city][car][feature]:
                            if t[0] not in (filter_list+car1_label) and t[1] > 0:
                                f.write('%s\t%s\t%s\t%s\t%s\n' % (str(city), str(
                                    car), str(feature), str(t[0]), str(t[1])))
                    elif int(car) == 5:
                        for label in car5_label:
                            f.write('%s\t%s\t%s\t%s\t%s\n' % (str(city), str(
                                car), str(feature), str(label), str(1000.0)))
                        for t in lab_rec[city][car][feature]:
                            if t[0] not in (filter_list+car5_label) and t[1] > 0:
                                f.write('%s\t%s\t%s\t%s\t%s\n' % (str(city), str(
                                    car), str(feature), str(t[0]), str(t[1])))
                    elif int(car) == 0:
                        for label in car0_label:
                            f.write('%s\t%s\t%s\t%s\t%s\n' % (str(city), str(
                                car), str(feature), str(label), str(1000.0)))
                        for t in lab_rec[city][car][feature]:
                            if t[0] not in (filter_list+car0_label) and t[1] > 0:
                                f.write('%s\t%s\t%s\t%s\t%s\n' % (str(city), str(
                                    car), str(feature), str(t[0]), str(t[1])))
                    else:
                        f.write('%s\t%s\t%s\t%s\t%s\n' % (str(city), str(
                            car), str(feature), str('加长'), str(1000.0)))
                        for t in lab_rec[city][car][feature]:
                            if t[0] not in filter_list and t[0] != '加长' and t[1] > 0:
                                f.write('%s\t%s\t%s\t%s\t%s\n' % (str(city), str(
                                    car), str(feature), str(t[0]), str(t[1])))

def main():
    head = 'poi'
    load_json()
    show_click_num = merge_data(head)
    write_file(head, show_click_num)

if __name__ == '__main__':
    main()