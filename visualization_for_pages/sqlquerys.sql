WITH location_data AS (
    SELECT 
        loc.id AS location_id,
        loc.municipality,
        loc.district,
        loc.street_address,
        loc.longitude,
        loc.latitude
    FROM dim_location loc
),
apartment_data AS (
    SELECT 
        ap.id AS apartment_id,
        ap.floor,
        ap.rooms,
        ap.floor_area,
        ap.balcony,
        ap.elevator,
        fct.location_id,
        apt.is_youth,
        apt.is_senior
    FROM dim_apartment ap
    JOIN fct_ad fct
    ON ap.id = fct.apartment_id
    JOIN dim_apartment_type apt
    ON fct.apartment_type_id = apt.id
),
ad_data AS (
    SELECT 
        fct.ad_id,
        fct.rent,
        fct.location_id,
        ad.published,
        ad.lease_type  -- Lägg till lease_type här
    FROM fct_ad fct
    JOIN dim_ad ad
    ON fct.ad_id = ad.id
)
SELECT 
    loc.municipality,
    loc.district,
    loc.longitude,
    loc.latitude,
    ap.rooms,
    ap.floor_area,
    ap.balcony,
    ap.elevator,
    ap.is_youth,
    ap.is_senior,
    ad.rent,
    ad.published,
    ad.lease_type  -- Lägg till lease_type här också
FROM location_data loc
JOIN apartment_data ap
ON loc.location_id = ap.location_id
JOIN ad_data ad
ON loc.location_id = ad.location_id;
