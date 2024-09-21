from kinscare_chat.database.core_mongo import MongoDbSession

read_db = MongoDbSession('read')
write_db = MongoDbSession('write')
