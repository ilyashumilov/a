GENDER_AGE_QUERY = 'select age, SUM(CASE WHEN gender_id = 1 THEN 1 ELSE 0 END) as male, SUM(CASE WHEN gender_id = 2 THEN 1 ELSE 0 END) as female,COUNT(*) as total FROM hype__subscriber WHERE bloggers && array[{}]::bigint[] GROUP by age'
GENDER_QUERY = 'select SUM(CASE WHEN gender_id = 1 THEN 1 ELSE 0 END) as male, SUM(CASE WHEN gender_id = 2 THEN 1 ELSE 0 END) as female,COUNT(*) as total FROM hype__subscriber WHERE bloggers && array[{}]::bigint[]'

MASS_FOLLOWERS_PART_QUERY = "SUM(CASE WHEN following > 1000 THEN 1 ELSE 0 end) as mass_followers"
QUALITY_PART_QUERY = "SUM(CASE WHEN (followers > 1000 and followers < 10000 and (contents is not null and contents != 0) and avatar is not NULL) THEN 1 ELSE 0 end) as quality_subscribers"
SUSPICIOUS_PART_QUERY = "SUM(CASE WHEN ((followers > 1000 or ((contents=0 or contents is NULL) and avatar is NULL) and following is not null)) THEN 1 ELSE 0 end) as suspicious_accounts"
BUSINESSES_PART_QUERY = "SUM(CASE WHEN is_business_account=TRUE THEN 1 ELSE 0 end) as suspicious_accounts"
INFLUENTIAL_PART_QUERY = "SUM(CASE WHEN followers > 1000000 THEN 1 ELSE 0 end) as influential"

AUDIENCE_TEMPLATE_QUERY = "SELECT {} FROM hype__subscriber WHERE bloggers && array[{}]::bigint[]"

BIO_QUERY = "SELECT bio FROM hype__subscriber WHERE bloggers && array[{}]::bigint[] and bio is not NULL limit 300000"

CITY_QUERY = 'SELECT Max(main_address."native_city") as name, COUNT(*) as count FROM hype__subscriber psb left join main_address on main_address.city_id = psb.address_id  WHERE bloggers && array[{}]::bigint[] and psb.address_id is not null GROUP BY address_id'
COUNTRY_QUERY = 'SELECT Max(main_address."native_country") as name, COUNT(*) as count FROM hype__subscriber psb left join main_address on main_address.city_id = psb.address_id WHERE bloggers && array[{}]::bigint[] and psb.address_id is not null GROUP BY address_id'

LANGUAGE_QUERY = 'SELECT Max(hype_language.native_name), COUNT(*) as count FROM hype__subscriber psb left join hype_language on hype_language.id = psb.language_id WHERE bloggers && array[{}]::bigint[] and psb.language_id is not null GROUP BY language_id'


def lang_query_replace(q: str, lang: str):
    if lang == 'ru':
        return q
    else:
        q = q.replace('native_', 'original_')
        return q
