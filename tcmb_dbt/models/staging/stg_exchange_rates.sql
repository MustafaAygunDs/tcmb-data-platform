with source as (
    select * from {{ source('staging', 'stg_exchange_rates') }}
),

renamed as (
    select
        id,
        tarih                   as rate_date,
        unvan                   as series_code,
        deger                   as rate_value,
        sma_7,
        volatility_7,
        created_at
    from source
    where tarih is not null
      and deger is not null
)

select * from renamed
