-- get date, start_time, duration, nap_id for every date in range of data
WITH each_date AS  -- get every date in range of data
(SELECT i::date FROM generate_series((SELECT MIN(start_date) FROM sl_night), (SELECT MAX(start_date) FROM sl_night), '1 day'::interval) i)
,
everything AS  -- get all fields from both sl_night and sl_nap
(SELECT sl_night.night_id AS ni_ni_id, start_date, sl_night.start_time AS ni_time,
nap_id, sl_nap.start_time AS na_time, duration, sl_nap.night_id AS na_ni_id
FROM sl_night JOIN sl_nap ON sl_night.night_id = sl_nap.night_id)
-- put nulls into output when there is no data for a date
SELECT each_date.i::date AS sleep_date, 
    everything.na_time as nap_time, 
    everything.duration AS duration,
    everything.nap_id AS nap_id
FROM each_date
LEFT JOIN everything ON each_date.i::date = everything.start_date
ORDER BY sleep_date, nap_id;


-- note: if no bedtime happens on a calendar date, no data except for the date is output
