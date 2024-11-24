import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, User, Planet, Character, FavoritePlanet, FavoriteCharacter

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de la base de datos
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://", "postgresql://"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///starwars.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
MIGRATE = Migrate(app, db)
CORS(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route("/")
def sitemap():
    return generate_sitemap(app)


# Endpoints adicionales
@app.route("/people", methods=["GET"])
def get_all_people():
    characters = Character.query.all()
    return jsonify([char.serialize() for char in characters]), 200


@app.route("/people/<int:people_id>", methods=["GET"])
def get_character_by_id(people_id):
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"msg": "Personaje no encontrado"}), 404
    return jsonify(character.serialize()), 200


@app.route("/planets", methods=["GET"])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200


@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200


@app.route("/users", methods=["GET"])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    return jsonify(user.serialize()), 200


@app.route("/users/<int:user_id>/favorites", methods=["GET"])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    favorite_planets = [fav.planet.serialize() for fav in user.planet_favorites]
    favorite_characters = [
        fav.character.serialize() for fav in user.character_favorites
    ]
    return (
        jsonify({"planets": favorite_planets, "characters": favorite_characters}),
        200,
    )


@app.route("/favorite/planet/<int:planet_id>/<int:user_id>", methods=["POST"])
def add_favorite_planet(planet_id, user_id):
    favorite = FavoritePlanet(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "Planeta favorito añadido"}), 201


@app.route("/favorite/people/<int:people_id>/<int:user_id>", methods=["POST"])
def add_favorite_people(people_id, user_id):
    favorite = FavoriteCharacter(user_id=user_id, character_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "Personaje favorito añadido"}), 201


@app.route("/favorite/planet/<int:planet_id>/<int:user_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id, user_id):
    favorite = FavoritePlanet.query.filter_by(
        user_id=user_id, planet_id=planet_id
    ).first()
    if not favorite:
        return jsonify({"msg": "Favorito no encontrado"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Planeta favorito eliminado"}), 200


@app.route("/favorite/people/<int:people_id>/<int:user_id>", methods=["DELETE"])
def delete_favorite_people(people_id, user_id):
    favorite = FavoriteCharacter.query.filter_by(
        user_id=user_id, character_id=people_id
    ).first()
    if not favorite:
        return jsonify({"msg": "Favorito no encontrado"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Personaje favorito eliminado"}), 200


# Endpoint para agregar un personaje
@app.route("/people", methods=["POST"])
def add_character():
    data = request.get_json()
    new_character = Character(
        name=data["name"],
        description=data["description"],
    )
    db.session.add(new_character)
    db.session.commit()
    return jsonify({"msg": "Personaje agregado correctamente"}), 201


# Endpoint para agregar un planeta
@app.route("/planets", methods=["POST"])
def add_planet():
    data = request.get_json()
    new_planet = Planet(
        name=data["name"],
        description=data["description"],
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"msg": "Planeta agregado correctamente"}), 201


# Endpoint para eliminar un personaje
@app.route("/people/<int:people_id>", methods=["DELETE"])
def delete_character(people_id):
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"msg": "Personaje no encontrado"}), 404
    db.session.delete(character)
    db.session.commit()
    return jsonify({"msg": "Personaje eliminado correctamente"}), 200


# Endpoint para eliminar un planeta
@app.route("/planets/<int:planet_id>", methods=["DELETE"])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planeta no encontrado"}), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"msg": "Planeta eliminado correctamente"}), 200


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=False)
