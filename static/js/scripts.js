function addSpecies() {
    const speciesContainer = document.getElementById('species-container');

    // Create new species fields
    const speciesInput = document.createElement('input');
    speciesInput.type = 'text';
    speciesInput.name = 'species[]';
    speciesInput.placeholder = 'Species Name';
    speciesInput.required = true;

    const countInput = document.createElement('input');
    countInput.type = 'number';
    countInput.name = 'count[]';
    countInput.placeholder = 'Count';
    countInput.required = true;

    // Create a remove button only after a new species is added
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.textContent = 'Remove Species';
    removeButton.onclick = function () {
        speciesContainer.removeChild(speciesInput);
        speciesContainer.removeChild(countInput);
        speciesContainer.removeChild(removeButton);
    };

    // Append new elements to the species container
    speciesContainer.appendChild(speciesInput);
    speciesContainer.appendChild(countInput);
    speciesContainer.appendChild(removeButton);
}
