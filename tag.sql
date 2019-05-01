set hive.cli.print.header=true;
select user_id, city_id, driver_id, logtime, car_type, start_address_gps, CONCAT_WS("|", CAST(user_id as STRING), start_address_gps, car_type) as mix, labels, context_json, dt from(
select user_id, city_id, driver_id, get_json_object(context_json, '$.car_type_id') as car_type, CONCAT_WS(" ", CONCAT_WS("-", regexp_extract(get_json_object(context_json,'$.logtime'), '([0-9]{4})([0-9]{2})([0-9]{2})-([0-9]{2}:[0-9]{2}:[0-9]{2})', 1), regexp_extract(get_json_object(context_json,'$.logtime'), '([0-9]{4})([0-9]{2})([0-9]{2})-([0-9]{2}:[0-9]{2}:[0-9]{2})', 2), regexp_extract(get_json_object(context_json,'$.logtime'), '([0-9]{4})([0-9]{2})([0-9]{2})-([0-9]{2}:[0-9]{2}:[0-9]{2})', 3)), regexp_extract(get_json_object(context_json,'$.logtime'), '([0-9]{4})([0-9]{2})([0-9]{2})-([0-9]{2}:[0-9]{2}:[0-9]{2})', 4)) as logtime, get_json_object(context_json, '$.start_address_gps') as start_address_gps, get_json_object(context_json,'$.labels') as labels, context_json, dt from sy_ods_flow.f_agt_prediction_business
where dt>='2019-01-23' and prediction_business_name='label_match') as a

limit 20000000;
