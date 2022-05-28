def get_user_schema():
    return {
            "bsonType": "object",
            "required": ["username", "email", "password", "name"],
            "properties": {
                "name": {"type": "string", "pattern": "[A-Za-z\s]*"},
                "email": {"type": "string", "pattern": "[a-z0-9]{5,15}"},
                "username": {"type": "string", "pattern": "[a-z0-9]{5,15}"},
                "password": {"type": "string", "pattern": "[a-zA-Z0-9]{5,15}"},
                "age": {"type": "integer", "minimum": 0, "maximum":110}
            }
        }

def get_audios_schema():
    return {
            "bsonType": "object",
            "required": ["user_id"],
            "properties": {
                "audio_name": {"type": "string"},
                "upload_date": {"type": "string"},
                "user_id": {"type": "string"}
            }
        }
