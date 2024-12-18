WITH source_location AS (SELECT * FROM {{ ref('source_location') }})

SELECT 
    ROW_NUMBER() OVER (ORDER BY (1)) AS id,
    municipality,
    district,
    street_address,
    longitude,
    latitude

FROM source_location