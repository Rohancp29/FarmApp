function addSpecies() {
    const container = document.getElementById('species-container');
    const newSpecies = document.createElement('div');
    newSpecies.innerHTML = `
        <input type="text" name="species[]" placeholder="Species Name" required>
        <input type="number" name="count[]" placeholder="Count" required><br><br>
    `;
    container.appendChild(newSpecies);
}

document.getElementById('homeForm').addEventListener('submit', function (event) {
    const contactNumber = document.getElementById('contact_number').value.trim();
    const plotLocation = document.getElementById('plot_location').value.trim();
    const fieldPhoto = document.getElementById('field_photo').files.length;

    
    if (!/^\d{10}$/.test(contactNumber)) {
        alert('Contact Number must be exactly 10 digits.');
        event.preventDefault();  
        return;
    }

    if (!plotLocation) {
        alert('Plot Location is required.');
        event.preventDefault();  
        return;
    }

    if (fieldPhoto === 0) {
        alert('Please upload a field photo.');
        event.preventDefault(); 
        return;
    }
});
