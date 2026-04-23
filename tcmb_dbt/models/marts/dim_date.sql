with dates as (
    select distinct rate_date from {{ ref('stg_exchange_rates') }}
)

select
    rate_date                               as date_id,
    extract(year  from rate_date)::int      as year,
    extract(month from rate_date)::int      as month,
    extract(day   from rate_date)::int      as day,
    extract(week  from rate_date)::int      as week,
    to_char(rate_date, 'Day')               as day_name,
    to_char(rate_date, 'Month')             as month_name,
    case
        when extract(dow from rate_date) in (0, 6) then false
        else true
    end                                     as is_weekday
from dates
order by date_id
