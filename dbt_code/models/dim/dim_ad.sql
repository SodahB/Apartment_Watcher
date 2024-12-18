WITH source_ad AS (SELECT * FROM {{ ref('source_ad') }})

SELECT 
    ROW_NUMBER() OVER (ORDER BY (1)) AS id,
    bf_ad_id,
    url,
    lease_type,
    published,
    deadline

FROM source_ad