
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('id_foto').onchange = function () {
        var src = URL.createObjectURL(this.files[0]);
        document.getElementById('image').src = src;
        document.getElementById('btnSearch').hidden = false;
        document.getElementById('ai_result').hidden = false;
    };
});


function toUpper(str) {
    if (typeof str !== 'string' || str.length === 0) return str;
    return str
        .toLowerCase()
        .split(' ')
        .map(word => word.length ? word[0].toUpperCase() + word.slice(1) : word)
        .join(' ');
}

function setField(id, value) {
    const el = document.getElementById(id);
    if (!el || value === undefined || value === null) return;
    el.value = value;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
}

function populateForm(data) {
    const ovData = JSON.parse(data);

    setField('id_domein', toUpper(ovData.wine_domain));
    setField('id_naam', toUpper(ovData.name));
    setField('id_jaar', ovData.year);
    setField('id_land', ovData.country);
    setField('id_streek', ovData.region);
    setField('id_classificatie', ovData.classification);
    setField('id_opmerking', ovData.description);
    setField('id_website', ovData.domain_website_url);

    // Wijnsoort select (Select2)
    const wijnsoortSelect = document.getElementById('id_wijnsoort');
    const matchingOption = Array.from(wijnsoortSelect.options)
        .find(option => option.textContent.trim() === ovData.wine_type);
    if (matchingOption) {
        wijnsoortSelect.value = matchingOption.value;
        wijnsoortSelect.dispatchEvent(new Event('change', { bubbles: true }));
        console.log("Matching wine type found:", matchingOption.value);
    } else {
        console.warn("No matching wine type found for:", ovData.wine_type);
    }

    // Druivensoorten multi-select (Select2)
    const druivenSelect = document.getElementById('id_wijnDruivensoorten');
    const druifOpties = Array.from(druivenSelect.options);
    druifOpties.forEach(option => option.selected = false);
    (ovData.grape_varieties || []).forEach(druif => {
        const match = druifOpties.find(opt =>
            opt.textContent.trim().toLowerCase() === druif.toLowerCase()
        );
        if (match) match.selected = true;
    });
    druivenSelect.dispatchEvent(new Event('change', { bubbles: true }));

    const firstField = document.getElementById('id_domein');
    if (firstField) firstField.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function callPythonFunction() {
    const baseUrl = `${window.location.protocol}//${window.location.host}`;
    const fileInput = document.getElementById('id_foto'); // Verwijst naar het file-input element
    const imageFile = fileInput.files[0]; // Het geselecteerde bestand
    const btnSearch = document.getElementById('btnSearch');

    btnSearch.disabled = true;
    btnSearch.textContent = "Bezig met zoeken...";
    setTimeout(() => {
        btnSearch.disabled = true;
        btnSearch.textContent = "Bezig met zoeken...";
    }, 2);

    if (!imageFile) {
        alert("Selecteer een afbeelding voordat je zoekt.");
        return;
    }

    const formData = new FormData();
    formData.append('image', imageFile); // Voeg de afbeelding toe aan FormData

    fetch(baseUrl + '/AI-zoeken/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // CSRF-token toevoegen
        }
    })
        .then( async response => {
            if (!response.ok) {
                // Probeer error-body te lezen
                let errorData;
                try {
                    errorData = await response.json();
                } catch {
                    errorData = { message: 'Onbekende serverfout' };
                }

                throw {
                    status: response.status,
                    message: errorData.message || 'Request failed',
                };

            }
        return response.json();
    })
    .then(data => {
        populateForm(data.message);
        document.getElementById('ai_result').textContent = data.message;
                
        })
    .catch(error => {
        console.error('Error:', error);

        const errorMessage = error.message || 'Er is een fout opgetreden';
        document.getElementById('ai_result').textContent = errorMessage;
        alert('Er is een fout opgetreden, check ai_result field');
    })
    .finally(() => {
        if (btnSearch) {
            btnSearch.disabled = false;
            btnSearch.textContent = "Zoeken";
        }
        
    });
}

