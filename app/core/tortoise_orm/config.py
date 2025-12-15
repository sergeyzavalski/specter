from core.settings import get_settings

settings = get_settings()


DB_CONFIG = {
    "connections": {
        "default": {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': settings.postgres_api.HOST,
                'port': settings.postgres_api.PORT,
                'user': settings.postgres_api.USER,
                'password': settings.postgres_api.PASS,
                'database': settings.postgres_api.NAME,
            },
            'maxsize': 25,
        },
    },
    "apps": {
        "models": {
            "models": settings.app.API_TORTOISE_MODELS + ["aerich.models"],
            "default_connection": "default",
        },
    },
}
