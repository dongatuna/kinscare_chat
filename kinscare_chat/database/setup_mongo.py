from pymongo import MongoClient
import os

def setup_mongo():
    config = {
        'mongodb_uri': os.getenv('MONGODB_URI'),
        'db_name': os.getenv('MONGODB_DB_NAME'),
        'db_username': os.getenv('MONGODB_USERNAME'),
        'db_password': os.getenv('MONGODB_PASSWORD'),
        'auth_source': os.getenv('MONGODB_AUTH_SOURCE', 'admin')
    }

    client = MongoClient(
        config['mongodb_uri'],
        username=config['db_username'],
        password=config['db_password'],
        authSource=config['auth_source'],
        connectTimeoutMS=60000,
        serverSelectionTimeoutMS=60000,
    )

    db = client[config['db_name']]

    # Define the collection names and validation rules
    collections = {
        'users': {
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['ext_user_id', 'settings'],
                    'properties': {
                        'ext_user_id': {
                            'bsonType': 'string',
                            'description': 'External user ID must be a string and is required'
                        },
                        'settings': {
                            'bsonType': 'object',
                            'description': 'Settings must be a document and is required',
                            'properties': {
                                'share_emails': {
                                    'bsonType': 'array',
                                    'items': {
                                        'bsonType': 'string'
                                    },
                                    'description': 'share_emails must be an array of strings'
                                }
                            },
                            'additionalProperties': True
                        }
                    },
                    'additionalProperties': True
                }
            }
        },
        'fb_creds': {
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['user_id', 'access_token'],
                    'properties': {
                        'user_id': {
                            'bsonType': 'objectId',
                            'description': 'User ID must be an ObjectId and is required'
                        },
                        'access_token': {
                            'bsonType': 'string',
                            'description': 'Access token must be a string and is required'
                        },
                        'token_type': {
                            'bsonType': 'string',
                            'description': 'Token type must be a string'
                        },
                        'expires_in': {
                            'bsonType': 'int',
                            'description': 'Expires in must be an integer'
                        },
                        'created_at': {
                            'bsonType': 'date',
                            'description': 'Created at must be a date'
                        }
                    },
                    'additionalProperties': True
                }
            }
        },
        'ig_creds': {
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['user_id', 'access_token'],
                    'properties': {
                        'user_id': {
                            'bsonType': 'objectId',
                            'description': 'User ID must be an ObjectId and is required'
                        },
                        'access_token': {
                            'bsonType': 'string',
                            'description': 'Access token must be a string and is required'
                        },
                        'token_type': {
                            'bsonType': 'string',
                            'description': 'Token type must be a string'
                        },
                        'expires_in': {
                            'bsonType': 'int',
                            'description': 'Expires in must be an integer'
                        },
                        'created_at': {
                            'bsonType': 'date',
                            'description': 'Created at must be a date'
                        }
                    },
                    'additionalProperties': True
                }
            }
        },
        'programs': {
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['program_data'],
                    'properties': {
                        'program_data': {
                            'bsonType': 'object',
                            'description': 'Program data must be a document and is required',
                            'additionalProperties': True
                        }
                    },
                    'additionalProperties': True
                }
            }
        },
        'saved_programs': {
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['program_id'],
                    'properties': {
                        'program_id': {
                            'bsonType': 'objectId',
                            'description': 'Program ID must be an ObjectId and is required'
                        }
                    },
                    'additionalProperties': True
                }
            }
        },
        'plans': {
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['user_id', 'saved_prog_id'],
                    'properties': {
                        'user_id': {
                            'bsonType': 'objectId',
                            'description': 'User ID must be an ObjectId and is required'
                        },
                        'saved_prog_id': {
                            'bsonType': 'objectId',
                            'description': 'Saved Program ID must be an ObjectId and is required'
                        },
                        'content': {
                            'bsonType': 'string',
                            'description': 'Content must be a string'
                        },
                        'created_at': {
                            'bsonType': 'date',
                            'description': 'Created at must be a date'
                        }
                    },
                    'additionalProperties': True
                }
            }
        }
    }

    # Create collections if they do not exist, with validation
    existing_collections = db.list_collection_names()

    for collection_name, options in collections.items():
        if collection_name not in existing_collections:
            db.create_collection(collection_name, validator=options['validator'])
            print(f"Created collection with validation: {collection_name}")
        else:
            print(f"Collection already exists: {collection_name}")
            # Optionally update the validator if needed
            db.command({
                'collMod': collection_name,
                'validator': options['validator'],
                'validationLevel': 'moderate'  # Or 'strict' or 'off'
            })

if __name__ == "__main__":
    setup_mongo()
