
def get_query_payins(start, end, currency):
    return f'''
--unpack json format
with cte_json as
(select paymentid,
json_array_elements_text(gross_currency) as g_currency,json_array_elements_text(gross_amount)::float as g_amount,
json_array_elements_text(revenue_currency) as n_currency,json_array_elements_text(revenue_amount)::float as n_amount
from public.payment
),
--get gross value
gross as
(select paymentid, g_currency, g_amount 
from cte_json
where g_currency = '{currency}'
),
--get net value
net as
(select paymentid, n_currency, n_amount 
from cte_json
where n_currency = '{currency}'
),
all_data AS
(select DATE(registertime - interval '1 hour') as register_date
, DATE(paymenttime - interval '1 hour') as payment_date
, g_amount
, n_amount
from public.payment a 
left join gross b USING(paymentid)
left join net c USING(paymentid)
-- filter rejects, discards, rollbacks
where a.paymentid not in (select paymentid 
	from public.payment
	where rejecttime is not null 
	or discardtime is not null
	or rollbacktime is not null)
and a.registertime - interval '1 hour' between '{start} 00:00:00.000' and '{end} 23:59:59.999'
),
all_data_group as 
(select register_date, payment_date, SUM(g_amount) as g_amount, SUM(n_amount) as n_amount
from all_data
group by 1,2
),
-- create all days for join
all_days as 
(SELECT * 
FROM (
   SELECT generate_series(min(registertime), NOW() - interval '1 day', '1d')::date AS register_date
   FROM   public.payment
   ) a
cross join (
   SELECT generate_series(min(registertime), NOW() - interval '1 day', '1d')::date AS payment_date
   FROM   public.payment
   ) b
where register_date <= payment_date
 )
 select a.register_date
 , c.installs
 , a.payment_date
 , SUM(g_amount) over (partition by a.register_date order by a.payment_date)/c.installs as rolling_gross_ltv
 , SUM(n_amount) over (partition by a.register_date order by a.payment_date)/c.installs as rolling_net_ltv
 , row_number() over (partition by a.register_date order by a.payment_date) as date_number
 from all_days a 
 left join all_data_group b on a.register_date = b.register_date and a.payment_date = b.payment_date
 left join 
	( select DATE(registertime - interval '1 hour') as register_date, COUNT(*) as installs
	from player p 
	group by 1) c on a.register_date = c.register_date
 where a.register_date between '{start} 00:00:00.000' and '{end} 23:59:59.999'
'''

