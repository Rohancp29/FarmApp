from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import os
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient("mongodb+srv://rohanpatil:Patil2909@farmapp.wuxmi.mongodb.net/?retryWrites=true&w=majority&appName=Farmapp")
db = client['FarmApp']
users_collection = db['users']
farmer_data_collection = db['farmer_data']

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    name = request.form['name'].strip()
    role = request.form['role'].strip()
    password = request.form['password'].strip()

    user = users_collection.find_one({"name": name, "role": role, "password": password})
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

    data = {
        "farmer_name": request.form['farmer_name'],
        "contact_number": request.form['contact_number'],
        "plot_location": request.form['plot_location'],
        "tree_species": species_list,  # Tree species names
        "species_count": count_list,  # Corresponding species counts
        "submitted_by": session['member_name'],
        "updated_by": None
    }

    # Handle file upload
    file = request.files['field_photo']
    if file:
        filename = file.filename
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        data['field_photo'] = file_path

    farmer_data_collection.insert_one(data)
    return redirect(url_for('home'))

@app.route('/view_data')
def view_data():
    if 'member_name' not in session:
        return redirect(url_for('login'))

    role = session['role']
    member_name = session['member_name']
    data = []

    # Role-based data access
    if role == "Field Executive":
        data = farmer_data_collection.find({"submitted_by": member_name})
    elif role == "Field Manager" and member_name == "C":
        data = farmer_data_collection.find({"submitted_by": {"$in": ["A", "B", "C"]}})
    elif role == "Field Manager" and member_name == "D":
        data = farmer_data_collection.find({"submitted_by": "D"})
    elif role == "Senior Manager":
        data = farmer_data_collection.find()
    else:
        data = farmer_data_collection.find({"submitted_by": None})

    data_list = list(data)

    return render_template('view_data.html', data=data_list, name=member_name, role=role)

@app.route('/edit_data/<data_id>', methods=['GET', 'POST'])
def edit_data(data_id):
    if 'member_name' not in session or session['role'] != "Senior Manager":
        return redirect(url_for('login'))

    if request.method == 'POST':
        update_data = {
            "farmer_name": request.form['farmer_name'],
            "contact_number": request.form['contact_number'],
            "plot_location": request.form['plot_location'],
            "tree_species": dict(zip(request.form.getlist('species[]'), request.form.getlist('count[]'))),
            "updated_by": session['member_name']
        }
        farmer_data_collection.update_one({"_id": ObjectId(data_id)}, {"$set": update_data})
        return redirect(url_for('view_data'))

    data = farmer_data_collection.find_one({"_id": ObjectId(data_id)})
    return render_template('edit_data.html', data=data)

@app.route('/delete_data/<data_id>', methods=['POST'])
def delete_data(data_id):
    if 'member_name' not in session or session['role'] != "Senior Manager":
        return redirect(url_for('login'))
    farmer_data_collection.delete_one({"_id": ObjectId(data_id)})
    return redirect(url_for('view_data'))



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
