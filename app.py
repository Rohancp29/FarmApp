from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import os
from bson import ObjectId
from opencage.geocoder import OpenCageGeocode
from werkzeug.utils import secure_filename
from pprint import pprint


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
 
client = MongoClient("mongodb+srv://rohanpatil:Patil2909@farmapp.wuxmi.mongodb.net/?retryWrites=true&w=majority&appName=Farmapp")
db = client['FarmApp']
users_collection = db['users']
farmer_data_collection = db['farmer_data']

geocoder = OpenCageGeocode('9ceef2fbe59c4197ace5a70f35d0cc22')


def get_address_from_coordinates(lat, lng):
    results = geocoder.reverse_geocode(lat, lng)
    if results and len(results) > 0:
        return results[0]['formatted']  
    return None  


@app.route('/')
def login():
    return render_template('login.html')



@app.route('/login', methods=['POST'])
def handle_login():
    name = request.form['name'].strip()
    password = request.form['password'].strip()
    user = users_collection.find_one({"name": name, "password": password})

    if user:
        session['member_name'] = user['name']
        session['role'] = user['role']
        return redirect(url_for('home'))

    return render_template('login.html', error="Invalid Credentials! Please try again.")



@app.route('/home')
def home():
    if 'member_name' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', name=session['member_name'], role=session['role'])


@app.route('/submit', methods=['POST'])
def submit_form():
    if 'member_name' not in session:
        return redirect(url_for('login'))
  
    species_list = request.form.getlist('species[]')
    count_list = request.form.getlist('count[]')
    farmer_name = request.form['farmer_name']
    contact_number = request.form['contact_number']
    plot_location = request.form['plot_location']  

    if not plot_location:
        return render_template('home.html', error={"plot_location": "Plot location is required."}, name=session['member_name'], role=session['role'])

    if not contact_number.isdigit() or len(contact_number) != 10:
        return render_template('home.html', error={"contact_number": "Contact number must be exactly 10 digits."}, name=session['member_name'], role=session['role'])
   
    file = request.files.get('field_photo')
    if file is None or file.filename == '':
        return render_template('home.html', error={"file": "Please upload a field photo."}, name=session['member_name'], role=session['role'])

    filename = secure_filename(file.filename)
    file_path = os.path.join('uploads', filename)
    file.save(file_path)
  
    data = {
        "farmer_name": farmer_name,
        "contact_number": contact_number,
        "plot_location": plot_location,  
        "tree_species": dict(zip(species_list, count_list)), 
        "submitted_by": session['member_name'],
        "updated_by": None,
        "field_photo": file_path
    }

    farmer_data_collection.insert_one(data)
    return redirect(url_for('home'))


@app.route('/view_data')
def view_data():
    if 'member_name' not in session:
        return redirect(url_for('login'))

    role = session['role']
    member_name = session['member_name']
    data = []

    role_conditions = {
        "Field Executive": {"submitted_by": member_name},
        "Field Manager": {
            "C": {"submitted_by": {"$in": ["A", "B", "C"]}},
            "D": {"submitted_by": "D"}
        },
        "Senior Manager": {}, 
    }

    if role == "Field Manager" and member_name in role_conditions[role]:
        query = role_conditions[role][member_name]
    else:
        query = role_conditions.get(role, {"submitted_by": None})

    data = farmer_data_collection.find(query)
    data_list = list(data)

    for entry in data_list:
        if isinstance(entry.get("tree_species"), list) and isinstance(entry.get("species_count"), list):
            entry["tree_species"] = dict(zip(entry["tree_species"], entry["species_count"]))
        elif not isinstance(entry.get("tree_species"), dict):
            entry["tree_species"] = {}

    return render_template('view_data.html', data=data_list, name=member_name, role=role)

@app.route('/edit_data/<data_id>', methods=['GET', 'POST'])
def edit_data(data_id):
    if 'member_name' not in session or session['role'] != "Senior Manager":
        return redirect(url_for('login'))

    if request.method == 'POST':
        updated_tree_species = dict(zip(
            request.form.getlist('species[]'),
            request.form.getlist('count[]')
        ))

        update_data = {
            "farmer_name": request.form['farmer_name'],
            "contact_number": request.form['contact_number'],
            "plot_location": request.form['plot_location'],
            "tree_species": updated_tree_species,
            "updated_by": session['member_name']
        }
        farmer_data_collection.update_one({"_id": ObjectId(data_id)}, {"$set": update_data})
        return redirect(url_for('view_data'))

    data = farmer_data_collection.find_one({"_id": ObjectId(data_id)})
    if data:
        if isinstance(data.get("tree_species"), list) and isinstance(data.get("species_count"), list):
            data["tree_species"] = dict(zip(data["tree_species"], data["species_count"]))
        elif not isinstance(data.get("tree_species"), dict):
            data["tree_species"] = {}

    return render_template('edit_data.html', data=data)

@app.route('/delete_data/<data_id>', methods=['POST'])    
def delete_data(data_id):
    if 'member_name' not in session or session['role'] != "Senior Manager":
        return redirect(url_for('login'))

    try:
        farmer_data_collection.delete_one({"_id": ObjectId(data_id)})
    except Exception as e:
        print(f"Error deleting entry: {e}")
    return redirect(url_for('view_data'))


@app.route('/delete_all_data', methods=['POST'])
def delete_all_data():
    if 'member_name' not in session or session['role'] != "Senior Manager":
        return redirect(url_for('login'))
    farmer_data_collection.delete_many({"submitted_by": session['member_name']})
    return redirect(url_for('view_data'))  


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
