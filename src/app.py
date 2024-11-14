import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import db, User, Planet, Character, FavoritePlanet, FavoriteCharacter

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


# Manejo de errores en JSON
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Sitemap
@app.route("/")
def sitemap():
    return generate_sitemap(app)


@app.route("/users", methods=["GET"])
def get_all_users():
    users = User.query.all()
    users_serialized = [user.serialize() for user in users]
    return jsonify({"msg": "ok", "data": users_serialized}), 200


@app.route("/planet", methods=["POST"])
def post_planet():
    body = request.get_json(silent=True)
    if body is None or "name" not in body or "climate" not in body:
        return jsonify({"msg": "Debe enviar nombre y clima en el body"}), 400
    new_planet = Planet(name=body["name"], climate=body["climate"])
    db.session.add(new_planet)
    db.session.commit()
    return (
        jsonify({"msg": "Planeta agregado con éxito", "data": new_planet.serialize()}),
        201,
    )


@app.route("/characters/<int:id>", methods=["GET"])
def get_characters(id):
    character = Character.query.get(id)
    if not character:
        return jsonify({"msg": "Personaje no encontrado"}), 404
    return jsonify({"msg": "ok", "data": character.serialize()}), 200


@app.route("/favorite_planets/<int:user_id>", methods=["GET"])
def get_favorites_by_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    favorite_planets = [fav.planet.serialize() for fav in user.planet_favorites]
    return (
        jsonify(
            {
                "msg": "ok",
                "data": {
                    "user_info": user.serialize(),
                    "planets_favorites": favorite_planets,
                },
            }
        ),
        200,
    )


# This only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=False)
