"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites, Clients, Leads
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def handle_hello():
    all_users = User.query.all()
    users = list(map(lambda x: x.serialize(), all_users))
    return jsonify(users), 200

@app.route('/users/<int:id>/favorites', methods=['GET'])
def get_user_fav(id):
    all_favorites = Favorites.query.filter_by(user_id = id)
    fav = list(map(lambda x: x.serialize(), all_favorites))
    return jsonify(fav), 200

@app.route('/users/<int:user_id>/favorites/client/<int:client_id>', methods=['POST'])
def post_favorite_client(user_id, client_id):
    favorite = Favorites(user_id = user_id, client_id = client_id, lead_id= "NULL")
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 200

@app.route('/users/<int:user_id>/favorites/lead/<int:lead>', methods=['POST'])
def post_favorite_lead(user_id, lead_id):
    favorite = Favorites(user_id = user_id, client_id = "NULL", lead_id= lead_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 200

@app.route('/users/<int:user_id>/favorites/client/<int:client_id>', methods=['DELETE'])
def delete_favorite_client(user_id, client_id):
    client = Favorites.query.filter_by(user_id = user_id, client_id = client_id).first()
    db.session.delete(client)
    db.session.commit()
    return jsonify("You deleted a favorite client")

@app.route('/users/<int:user_id>/favorites/lead/<int:lead_id>', methods=['DELETE'])
def delete_favorite_lead(user_id, lead_id):
    lead = Favorites.query.filter_by(user_id = user_id, lead_id = lead_id).first()
    db.session.delete(lead)
    db.session.commit()
    return jsonify("You deleted a favorite lead")

@app.route('/clients', methods=['GET'])
def get_all_clients():
    all_clients = Clients.query.all()
    clients = list(map(lambda x: x.serialize(), all_clients))
    return jsonify(clients), 200

@app.route('/clients/<int:client_id>', methods=['GET'])
def get_each_clients(client_id):
    client = Clients.query.filter_by(id = client_id).first()
    return jsonify(client.serialize())

@app.route('/leads', methods=['GET'])
def get_all_leads():
    all_leads = Leads.query.all()
    leads = list(map(lambda x: x.serialize(), all_leads))
    return jsonify(leads), 200

@app.route('/leads/<int:lead_id>', methods=['GET'])
def get_each_lead(lead_id):
    lead = Leads.query.filter_by(id = lead_id).first()
    return jsonify(lead.serialize())

@app.route('/clients', methods=['POST'])
def post_clients():
    data = request.get_json()
    client = Clients(name = data['name'], email = data['email'])
    db.session.add(client)
    db.session.commit()
    return jsonify(client.serialize()), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
