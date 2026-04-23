with stg as (
    select * from {{ ref('stg_exchange_rates') }}
),

dim_date as (
    select * from {{ ref('dim_date') }}
),

dim_series as (
    select * from {{ ref('dim_series') }}
),

joined as (
    select
        md5(stg.rate_date::text || '-' || stg.series_code) as fact_id,
        d.date_id,
        s.series_id,
        stg.rate_value                  as rate,
        stg.sma_7,
        stg.volatility_7                as volatility,
        stg.rate_value - lag(stg.rate_value) over (
            partition by stg.series_code
            order by stg.rate_date
        )                               as daily_change,
        round(
            (stg.rate_value - lag(stg.rate_value) over (
                partition by stg.series_code
                order by stg.rate_date
            )) / nullif(lag(stg.rate_value) over (
                partition by stg.series_code
                order by stg.rate_date
            ), 0) * 100,
        4)                              as daily_change_pct
    from stg
    inner join dim_date d on stg.rate_date = d.date_id
    inner join dim_series s on stg.series_code = s.series_code
)

select * from joined
