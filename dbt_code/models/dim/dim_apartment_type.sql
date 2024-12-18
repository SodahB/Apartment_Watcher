WITH source_apartment_type AS (SELECT * FROM {{ ref('source_apartment_type') }})

SELECT 
    ROW_NUMBER() OVER (ORDER BY (1)) AS id,
    is_youth,
    is_student,
    is_senior,
    is_short_term,
    is_youth_friendship,
    is_fast_track,
    is_limited_mobility,
    is_limited_orientation

FROM source_apartment_type