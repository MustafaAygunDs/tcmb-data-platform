with series as (
    select distinct series_code from {{ ref('stg_exchange_rates') }}
)

select
    row_number() over (order by series_code)    as series_id,
    series_code,
    case
        when series_code like '%USD%' then 'US Dollar / Turkish Lira'
        when series_code like '%EUR%' then 'Euro / Turkish Lira'
        when series_code like '%GBP%' then 'British Pound / Turkish Lira'
        when series_code like '%JPY%' then 'Japanese Yen / Turkish Lira'
        else series_code
    end                                         as series_name
from series
