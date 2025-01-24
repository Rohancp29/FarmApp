// Function to add new species and count input fields dynamically
function addSpecies() {
    const container = document.getElementById('species-container');
    const newSpecies = document.createElement('div');
    newSpecies.innerHTML = `
        <input type="text" name="species[]" placeholder="Species Name" required>
        <input type="number" name="count[]" placeholder="Count" required><br><br>
    `;
    container.appendChild(newSpecies);
}

// Function to validate the form before submission
document.getElementById('homeForm').addEventListener('submit', function (event) {
    const contactNumber = document.getElementById('contact_number').value.trim();
    const plotLocation = document.getElementById('plot_location').value.trim();
    const fieldPhoto = document.getElementById('field_photo').files.length;

    // Validate contact number: should be 10 digits
    if (!/^\d{10}$/.test(contactNumber)) {
        alert('Contact Number must be exactly 10 digits.');
        event.preventDefault();  // Prevent form submission
        return;
    }

    // Validate plot location: must not be empty
    if (!plotLocation) {
        alert('Plot Location is required.');
        event.preventDefault();  // Prevent form submission
        return;
    }

    // Validate field photo: file must be selected
    if (fieldPhoto === 0) {
        alert('Please upload a field photo.');
        event.preventDefault();  // Prevent form submission
        return;
    }
});
