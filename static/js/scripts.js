function addSpecies() {
    const section = document.getElementById("tree-species-section");
    const newField = `
        <div>
            <label>Tree Species:</label>
            <input type="text" name="species[]" required>
            <label>Count:</label>
            <input type="number" name="count[]" required>
        </div>`;
    section.insertAdjacentHTML("beforeend", newField);
}
