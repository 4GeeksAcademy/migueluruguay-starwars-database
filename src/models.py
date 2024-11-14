from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()


# Modelo de Usuario
class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(80), nullable=False)
    planet_favorites = relationship("FavoritePlanet", back_populates="user")
    character_favorites = relationship("FavoriteCharacter", back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }


# Modelo de Planeta
class Planet(db.Model):
    __tablename__ = "planet"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    climate = Column(String(50), nullable=False)
    population = Column(Integer)
    residents = relationship("Character", back_populates="home_planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population,
        }


# Modelo de Personaje
class Character(db.Model):
    __tablename__ = "character"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    species = Column(String(50))
    home_planet_id = Column(Integer, ForeignKey("planet.id"))
    home_planet = relationship("Planet", back_populates="residents")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "home_planet": self.home_planet.name if self.home_planet else None,
        }


# Modelo de Planetas Favoritos
class FavoritePlanet(db.Model):
    __tablename__ = "favorite_planet"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    planet_id = Column(Integer, ForeignKey("planet.id"))
    user = relationship("User", back_populates="planet_favorites")
    planet = relationship("Planet")


# Modelo de Personajes Favoritos
class FavoriteCharacter(db.Model):
    __tablename__ = "favorite_character"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    character_id = Column(Integer, ForeignKey("character.id"))
    user = relationship("User", back_populates="character_favorites")
    character = relationship("Character")
