"""Shared SQLAlchemy instance.

Kept in its own module so models and the app factory can both import it
without creating a circular dependency.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
