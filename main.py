from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_pour_session'
CORS(app)

DB_FILE = 'database.json'
USERS_FILE = 'users.json'
RENTALS_FILE = 'rentals.json'

# Initialiser les bases de données si elles n'existent pas
for file in [DB_FILE, USERS_FILE, RENTALS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump([], f)


def get_db(file):
    with open(file, 'r') as f:
        return json.load(f)


def save_db(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


# --- ROUTES DES PAGES ---

@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html')


@app.route('/admin')
@app.route('/admin.html')
def admin_page():
    return render_template('admin.html')


@app.route('/login')
def auth_page():
    return render_template('auth.html')


# --- ROUTES API APPLICATIONS ---

@app.route('/api/apps', methods=['GET'])
def get_apps():
    return jsonify(get_db(DB_FILE))


@app.route('/api/apps', methods=['POST'])
def add_app():
    new_app = request.json
    db = get_db(DB_FILE)
    app_entry = {
        "id": len(db) + 1,
        "name": new_app.get('name'),
        "desc": new_app.get('desc'),
        "price": new_app.get('price'),
        "url": new_app.get('url')
    }
    db.append(app_entry)
    save_db(DB_FILE, db)
    return jsonify(app_entry), 201


# --- ROUTES API UTILISATEURS ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    users = get_db(USERS_FILE)

    if any(u['email'] == data['email'] for u in users):
        return jsonify({"error": "Email déjà utilisé"}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = {
        "email": data['email'],
        "password": hashed_password,
        "rentals": []
    }
    users.append(new_user)
    save_db(USERS_FILE, users)
    return jsonify({"message": "Compte créé"}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    users = get_db(USERS_FILE)
    user = next((u for u in users if u['email'] == data['email']), None)

    if user and check_password_hash(user['password'], data['password']):
        session['user'] = user['email']
        return jsonify({"message": "Connecté", "email": user['email']}), 200

    return jsonify({"error": "Identifiants invalides"}), 401


@app.route('/api/logout')
def logout():
    session.pop('user', None)
    return jsonify({"message": "Déconnecté"})


@app.route('/api/me')
def get_me():
    if 'user' in session:
        return jsonify({"email": session['user']})
    return jsonify({"error": "Non connecté"}), 401


# --- ROUTES API LOCATIONS ---

@app.route('/api/rent', methods=['POST'])
def rent_app():
    if 'user' not in session:
        return jsonify({"error": "Vous devez être connecté pour louer"}), 401

    data = request.json
    app_id = data.get('app_id')
    user_email = session['user']

    rentals = get_db(RENTALS_FILE)

    # Création d'une nouvelle demande de location (statut 'pending' avant paiement)
    new_rental = {
        "id": len(rentals) + 1,
        "user_email": user_email,
        "app_id": app_id,
        "status": "pending",
        "date": "2026-04-06"  # On pourra dynamiser la date plus tard
    }

    rentals.append(new_rental)
    save_db(RENTALS_FILE, rentals)

    return jsonify({"message": "Demande de location enregistrée", "rental_id": new_rental['id']}), 201


@app.route('/api/my-rentals', methods=['GET'])
def get_my_rentals():
    if 'user' not in session:
        return jsonify({"error": "Non connecté"}), 401

    rentals = get_db(RENTALS_FILE)
    user_rentals = [r for r in rentals if r['user_email'] == session['user']]
    return jsonify(user_rentals)


if __name__ == '__main__':
    app.run(debug=True, port=5020)