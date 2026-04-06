from flask import Flask, request, jsonify, render_template # Ajout de render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DB_FILE = 'database.json'

# Initialiser la base de données si elle n'existe pas
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump([], f)

def get_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- ROUTES DES PAGES (Pour le navigateur) ---

@app.route('/')
def home():
    """Affiche le catalogue (index.html)"""
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    """Affiche le formulaire d'ajout (admin.html)"""
    return render_template('admin.html')

# --- ROUTES API (Pour les données) ---

@app.route('/api/apps', methods=['GET'])
def get_apps():
    """Récupère la liste de toutes les applications"""
    return jsonify(get_db())

@app.route('/api/apps', methods=['POST'])
def add_app():
    """Ajoute une nouvelle application au catalogue"""
    new_app = request.json
    db = get_db()

    app_entry = {
        "id": len(db) + 1,
        "name": new_app.get('name'),
        "desc": new_app.get('desc'),
        "price": new_app.get('price'),
        "url": new_app.get('url')
    }

    db.append(app_entry)
    save_db(db)
    return jsonify(app_entry), 201

if __name__ == '__main__':
    # On garde le port 5020 comme tu l'as configuré
    app.run(debug=True, port=5020)