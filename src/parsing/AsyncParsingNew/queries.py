PARSERS_QUERY = "SELECT * FROM account_parser WHERE account_type = $1;"
PARSER_BY_ID_QUERY = "SELECT * FROM account_parser WHERE id = $1;"
SUBSCRIBERS_EXISTS = "SELECT social_id FROM subscriber WHERE blogger_id = $1 AND social_id = ANY($2::bigint[]);"
POSTS_EXISTS = "SELECT post_id FROM post WHERE blogger_id = $1 and post_id = ANY($2::varchar[]);"
TIDS_EXISTS = "SELECT tid FROM main_tiddone WHERE tid = ANY($1::bigint[]);"
TID_SAVE = "INSERT INTO main_tiddone(tid) VALUES($1)"
BLOGGER_ID_BY_LOGIN = "SELECT id FROM Blogger WHERE login = $1"