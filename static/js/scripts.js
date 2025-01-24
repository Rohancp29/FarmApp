function addSpecies() {
    const speciesContainer = document.getElementById('species-container');
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


    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.textContent = 'Remove Species';
    removeButton.onclick = function () {
        speciesContainer.removeChild(speciesInput);
        speciesContainer.removeChild(countInput);
        speciesContainer.removeChild(removeButton);
    };
    
    speciesContainer.appendChild(speciesInput);
    speciesContainer.appendChild(countInput);
    speciesContainer.appendChild(removeButton);
}
