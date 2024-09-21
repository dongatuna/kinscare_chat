from kinscare_chat.database.core import DbSession

read_db = DbSession('read')
write_db = DbSession('write')
