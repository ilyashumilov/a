Q_EXISTS_SUBS_BY_SOCIAL_IDS = "SELECT id, social_id from parsing_subscriber where social_id = ANY($1::varchar[]);"
Q_EXISTS_SUBS_BY_ID_AND_BLOGGER = "SELECT subscriber_id from subscriber__bloggers where subscriber_id = ANY($1::bigint[]) and blogger_id = $2;"
