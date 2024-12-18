WITH stg_apartment_ads AS (SELECT * FROM {{ source('apartment_watcher', 'stg_apartment_ads') }})

SELECT 
    vaning AS floor,
    antal_rum AS rooms,
    yta AS floor_area,
    balkong AS balcony,
    hiss AS elevator,
    l_genhet_id AS bf_apartment_id
FROM stg_apartment_ads