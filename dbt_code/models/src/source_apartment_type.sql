WITH stg_apartment_ads AS (SELECT * FROM {{ source('apartment_watcher', 'stg_apartment_ads') }})

SELECT 
    ungdom AS is_youth,
    student AS is_student,
    senior AS is_senior,
    korttid AS is_short_term,
    kompis_ungdom AS is_youth_friendship,
    bostad_snabbt AS is_fast_track,
    tillganglig_nedsatt_rorelseformaga AS is_limited_mobility,
    tillganglig_nedsatt_orienteringsformaga AS is_limited_orientation
FROM stg_apartment_ads