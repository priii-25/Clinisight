import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aB9xY2zW8vK3jPqRtM5nL7hG4fD2cE6w'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost/clinisight'