import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    #Database Envs
    POSTGRES_HOST = os.getenv("database_host_url")
    POSTGRES_ADMIN_USER = os.getenv("database_admin_username")
    POSTGRES_ADMIN_PASSWORD = os.getenv("database_admin_password")
    POSTGRES_PORT = os.getenv("database_port") or 5432
    POSTGRES_DATABASE = os.getenv("database_name")
    DATABASE_DRIVER_NAME= os.getenv("database_driver_name")
    
    #Application / domain Envs
    SECRET_HASH_CODE = os.getenv("secret_hash_code")
    URL_DOMAIN = os.getenv("url_domain")

settings = Settings()