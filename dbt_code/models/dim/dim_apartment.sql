WITH source_apartment AS (SELECT * FROM {{ ref('source_apartment') }})

SELECT 
    ROW_NUMBER() OVER (ORDER BY (1)) AS id,
    floor,
    rooms,
    floor_area,
    balcony,
    elevator,
    bf_apartment_id

FROM source_apartment