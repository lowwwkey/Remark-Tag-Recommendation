set hive.cli.print.header=true;
select order_id,create_date,create_time,city_id,user_id,car_type,bi_state,
  start_biz_id,start_gps,CONCAT_WS("|", CAST(user_id as STRING), start_gps, CAST(car_type as STRING)) as mix, customer_service_remark, amaptag_first, amaptag_second, amaptag_thrid from(
select a.order_id, create_date, create_time, city_id, user_id, car_type, bi_state, start_biz_id, start_gps, customer_service_remark, amaptag_first, amaptag_second, amaptag_thrid from(
select order_id, create_date, create_time, city_id, user_id, car_type, bi_state, start_biz_id, start_gps, customer_service_remark
  from sy_dw_f.f_agt_order_info
  where create_date >= '2019-01-23') a
  left join
  (select dt, order_id, amaptag_first, amaptag_second, amaptag_thrid from daojia_ml.express_order_tag_amap where dt >='2010-01-23') b
  on a.order_id = b.order_id) c
  group by order_id,create_date,create_time,city_id,user_id,car_type,bi_state, start_biz_id,start_gps,customer_service_remark, amaptag_first, amaptag_second, amaptag_thrid
  order by user_id, create_date desc
  limit 20000000;
