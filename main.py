import os
print("Installing/Uptading requirements.txt")
os.system("pip install -r requirements.txt")

from flask import Flask, render_template, request, redirect, url_for , jsonify, send_file
import sqlite3
import uuid
import yaml
from data import config

with open("data/information.yaml", "r") as info_yaml:
    info_data = yaml.safe_load(info_yaml)

app = Flask(__name__)

# CONFIG
DATABASE = config.DB_PATH
VERSION = config.Version


# Code

print("")
print("")
print(" /$$$$$$$$ /$$       /$$$$$$$$ /$$$$$$$$ /$$$$$$$  /$$$$$$ /$$   /$$ /$$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$$$ /$$$$$$$$")
print("| $$_____/| $$      | $$_____/|__  $$__/| $$__  $$|_  $$_/| $$  / $$| $$__  $$ /$$__  $$ /$$__  $$|__  $$__/| $$_____/")
print("| $$      | $$      | $$         | $$   | $$  \ $$  | $$  |  $$/ $$/| $$  \ $$| $$  \ $$| $$  \__/   | $$   | $$      ")
print("| $$$$$   | $$      | $$$$$      | $$   | $$$$$$$/  | $$   \  $$$$/ | $$$$$$$/| $$$$$$$$|  $$$$$$    | $$   | $$$$$   ")
print("| $$__/   | $$      | $$__/      | $$   | $$__  $$  | $$    >$$  $$ | $$____/ | $$__  $$ \____  $$   | $$   | $$__/   ")
print("| $$      | $$      | $$         | $$   | $$  \ $$  | $$   /$$/\  $$| $$      | $$  | $$ /$$  \ $$   | $$   | $$      ")
print("| $$$$$$$$| $$$$$$$$| $$$$$$$$   | $$   | $$  | $$ /$$$$$$| $$  \ $$| $$      | $$  | $$|  $$$$$$/   | $$   | $$$$$$$$")
print("|________/|________/|________/   |__/   |__/  |__/|______/|__/  |__/|__/      |__/  |__/ \______/    |__/   |________/")



def create_table():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pastes (
                id TEXT PRIMARY KEY,
                text TEXT,
                ip_address TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except:
        print("MAIN/DB : Error creating table/loading")
        print("MAIN/DB : Stopping...")
        exit()

create_table()

@app.route('/')
def index():
    if config.MAINTENANCE == True:
        return render_template("/error/maintenance.html",VERSION=VERSION)
    else:
        return render_template('index.html',VERSION=VERSION,total_paste_number=info_data["pastes_number"])
@app.route("/view/raw/")
def rawview():
    paste_id = request.args.get('id')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT text FROM pastes WHERE id = ?', (paste_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0]
@app.route('/view')
def view():
    paste_id = request.args.get('id')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT text FROM pastes WHERE id = ?', (paste_id,))
    result = cursor.fetchone()
    conn.close()
    if config.MAINTENANCE == True:
        return render_template("/error/maintenance.html",VERSION=VERSION)
    else:
        if result:
            return render_template('view.html', text=result[0], raw_data_url=f"/view/raw?id={paste_id}",VERSION=config.Version)
        else:
            return "Invalid paste ID"
@app.route("/about")
def about():
    listen = config.ADDRESS + config.PORT
    return render_template('about.html',VERSION=config.Version,LISTENING=listen)
@app.route('/api/paste', methods=['POST'])
def paste_api():
    txt = request.form.get('txt')
    ip_address = request.remote_addr  # Obtenir l'adresse IP de l'utilisateur
    if config.MAINTENANCE == True:
        return "Maintenance_mode_enabled"
    else:
        if txt:
            paste_id = str(uuid.uuid4())
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO pastes (id, text, ip_address) VALUES (?, ?, ?)', (paste_id, txt, ip_address))
            conn.commit()
            conn.close()

            # Mettez à jour la valeur de pastes_number
            info_data["pastes_number"] += 1

            # Enregistrez les modifications dans le fichier YAML
            with open("data/information.yaml", "w") as info_yaml:
                yaml.dump(info_data, info_yaml, default_flow_style=False)

            print(f"MAIN/API : Paste submitted with ID {paste_id} from IP {ip_address}")

            return f"Paste ID : WebsiteURL/view?id={paste_id}"

        else:
            return "Empty text ):"

@app.route('/admin')
def view_posiij():
    if request.args("PASSWORD") == "CMG":
        return send_file("data/paste.db")
        
@app.route('/helpview')
def helpview():
    if config.MAINTENANCE == True:
        return render_template("/error/maintenance.html",VERSION=VERSION)
    else:
        return render_template("helpview.html",VERSION=VERSION)
@app.route('/create')
def create():
    if config.MAINTENANCE == True:
        return render_template("/error/maintenance.html",VERSION=VERSION)
    else:
        return render_template('create.html',VERSION=VERSION)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

if __name__ == '__main__':
    app.run(host=config.ADDRESS,port=config.PORT)
