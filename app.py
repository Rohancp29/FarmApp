from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import os
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to a secure secret key

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
        return redirect(url_for('home'))  # Redirect to home after successful login
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

    # Get form data
    species_list = request.form.getlist('species[]')
    count_list = request.form.getlist('count[]')
    farmer_name = request.form['farmer_name']
    contact_number = request.form['contact_number']
    plot_location = request.form['plot_location']

    # Validate contact number (should be 10 digits)
    if not contact_number.isdigit() or len(contact_number) != 10:
        # Return an error message and re-render the home page with the error message
        return render_template('home.html', error="Contact number must be exactly 10 digits.", name=session['member_name'], role=session['role'])

    # Validate plot location
    if not plot_location:
        return render_template('home.html', error="Plot location is required.", name=session['member_name'], role=session['role'])

    # Validate photo upload
    file = request.files.get('field_photo')
    if file is None or file.filename == '':
        return render_template('home.html', error="Please upload a field photo.", name=session['member_name'], role=session['role'])

    # Prepare the data to insert into MongoDB
    data = {
        "farmer_name": farmer_name,
        "contact_number": contact_number,
        "plot_location": plot_location,
        "tree_species": species_list,
        "species_count": count_list,
        "submitted_by": session['member_name'],
        "updated_by": None
    }

    # Handle file upload
    filename = file.filename
    file_path = os.path.join('uploads', filename)
    file.save(file_path)
    data['field_photo'] = file_path

    # Insert data into MongoDB
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

    # Normalize tree_species to a dictionary if it is a list
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

    # Retrieve the data for the given ID
    data = farmer_data_collection.find_one({"_id": ObjectId(data_id)})
    if data:
        # Ensure tree_species is in dictionary format for rendering
        if isinstance(data.get("tree_species"), list) and isinstance(data.get("species_count"), list):
            # Convert list of species and counts into a dictionary
            data["tree_species"] = dict(zip(data["tree_species"], data["species_count"]))
        elif not isinstance(data.get("tree_species"), dict):
            # If tree_species is not already a dictionary, initialize it as an empty one
            data["tree_species"] = {}

    return render_template('edit_data.html', data=data)

@app.route('/delete_data/<data_id>', methods=['POST'])    
def delete_data(data_id):
    if 'member_name' not in session or session['role'] != "Senior Manager":
        return redirect(url_for('login'))  # Redirect if session is not found or role doesn't match
    
    # Ensure we can convert the data_id to an ObjectId
    try:
        farmer_data_collection.delete_one({"_id": ObjectId(data_id)})
    except Exception as e:
        print(f"Error deleting entry: {e}")
    
    # Stay on the same page (view data)
    return redirect(url_for('view_data'))  # Redirect to the same view data page after deletion


@app.route('/delete_all_data', methods=['POST'])
def delete_all_data():
    # Ensure the user is logged in and has the correct role
    if 'member_name' not in session or session['role'] != "Senior Manager":
        return redirect(url_for('login'))  # Redirect if session is not found or role doesn't match
    
    # Delete all data submitted by the logged-in user (Field Executive)
    farmer_data_collection.delete_many({"submitted_by": session['member_name']})
    
    # Stay on the same page (view data)
    return redirect(url_for('view_data'))  # Redirect to the same view data page after deletion


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
