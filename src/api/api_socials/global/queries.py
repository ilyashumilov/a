GENDER_AGE_QUERY = 'select age, SUM(CASE WHEN gender_id = 1 THEN 1 ELSE 0 END) as male, SUM(CASE WHEN gender_id = 2 THEN 1 ELSE 0 END) as female,COUNT(*) as total FROM parsing_subscriber WHERE bloggers && array[{}]::bigint[] GROUP by age'
CITY_QUERY = 'SELECT Max(extra_city."native_name") as name, COUNT(*) as count FROM parsing_subscriber psb left join extra_city on extra_city.id = psb.city_id  WHERE bloggers && array[{}]::bigint[] and psb.city_id is not null GROUP BY city_id'
COUNTRY_QUERY = 'SELECT Max(extra_country."native_name") as name, COUNT(*) as count FROM parsing_subscriber psb left join extra_country on extra_country.id = psb.country_id WHERE bloggers && array[{}]::bigint[] and psb.country_id is not null GROUP BY country_id'
LANGUAGE_QUERY = 'SELECT language, COUNT(*) as count FROM parsing_subscriber psb WHERE bloggers && array[{}]::bigint[] and language is not null GROUP BY language'
GENDER_QUERY = 'select SUM(CASE WHEN gender_id = 1 THEN 1 ELSE 0 END) as male, SUM(CASE WHEN gender_id = 2 THEN 1 ELSE 0 END) as female,COUNT(*) as total FROM parsing_subscriber WHERE bloggers && array[{}]::bigint[]'

MASS_FOLLOWERS_PART_QUERY = "SUM(CASE WHEN following > 1000 THEN 1 ELSE 0 end) as mass_followers"
QUALITY_PART_QUERY = "SUM(CASE WHEN (followers > 1000 and followers < 10000 and (contents is not null and contents != 0) and avatar is not NULL) THEN 1 ELSE 0 end) as quality_subscribers"
SUSPICIOUS_PART_QUERY = "SUM(CASE WHEN ((followers > 1000 or ((contents=0 or contents is NULL) and avatar is NULL) and following is not null)) THEN 1 ELSE 0 end) as suspicious_accounts"
BUSINESSES_PART_QUERY = "SUM(CASE WHEN is_business_account=TRUE THEN 1 ELSE 0 end) as suspicious_accounts"
INFLUENTIAL_PART_QUERY = "SUM(CASE WHEN followers > 1000000 THEN 1 ELSE 0 end) as influential"

AUDIENCE_TEMPLATE_QUERY = "SELECT {} FROM parsing_subscriber WHERE bloggers && array[{}]::bigint[]"
