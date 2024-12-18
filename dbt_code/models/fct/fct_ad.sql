WITH fct_ads AS (SELECT * FROM {{ ref('src_ads') }}),

ad AS (SELECT * FROM {{ ref('dim_ad') }}),

apartment_type AS (SELECT * FROM {{ ref('dim_apartment_type') }}),

apartment AS (SELECT * FROM {{ ref('dim_apartment') }}),

l AS (SELECT * FROM {{ ref('dim_location') }})

SELECT 
    ad.id AS ad_id, 
    apartment.id AS apartment_id, 
    l.id AS location_id, 
    apartment_type.id AS apartment_type_id, 
    rent

FROM fct_ads
LEFT JOIN 
    ad ON fct_ads.id = ad.id
LEFT JOIN 
    apartment ON fct_ads.id = apartment.id
LEFT JOIN
    l ON fct_ads.id = l.id
LEFT JOIN
    apartment_type ON fct_ads.id = apartment_type.id
WHERE rent IS NOT NULL