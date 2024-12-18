WITH stg_apartment_ads AS (SELECT * FROM {{ source('apartment_watcher', 'stg_apartment_ads') }})

SELECT 
    kommun AS municipality,
    stadsdel AS district,
    gatuadress AS street_address,
    koordinat_longitud AS longitude,
    koordinat_latitud AS latitud
FROM stg_apartment_ads