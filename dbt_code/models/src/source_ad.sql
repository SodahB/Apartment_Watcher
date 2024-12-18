WITH stg_apartment_ads AS (SELECT * FROM {{ source('apartment_watcher', 'stg_apartment_ads') }})

SELECT
    annons_id AS bf_ad_id,
    url,
    lagenhetstyp AS lease_type,
    annonserad_fran AS published, 
    annonserad_till AS deadline

FROM stg_apartment_ads

