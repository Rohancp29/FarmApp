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

    if (!/^\d{10}$/.test(contactNumber)) {
        alert('Contact Number must be exactly 10 digits.');
        event.preventDefault();
    }
});
