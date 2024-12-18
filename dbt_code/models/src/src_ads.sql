WITH stg_apartment_ads AS (SELECT * FROM {{ source('apartment_watcher', 'stg_apartment_ads') }})

SELECT 
    ROW_NUMBER() OVER (ORDER BY (1)) AS id,
    hyra AS rent

FROM stg_apartment_ads