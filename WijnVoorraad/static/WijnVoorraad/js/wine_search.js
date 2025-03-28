
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('id_foto').onchange = function () {
        var src = URL.createObjectURL(this.files[0]);
        document.getElementById('image').src = src;
        document.getElementById('btnSearch').hidden = false;
        document.getElementById('ai_result').hidden = false;
    };
});


function toUpper(str) {
    return str
        .toLowerCase()
        .split(' ')
        .map(function(word) {
            return word[0].toUpperCase() + word.substr(1);
        })
        .join(' ');
}

function populateForm(data) {
    ovData = JSON.parse(data);
    document.getElementById('id_domein').value = toUpper(ovData.domain);
    document.getElementById('id_naam').value = toUpper(ovData.name);
    document.getElementById('id_jaar').value = ovData.year;
    document.getElementById('id_land').value = ovData.country;
    document.getElementById('id_streek').value = ovData.region;
    document.getElementById('id_classificatie').value = ovData.classification;

    // Wijnsoort selecteren
    const wijnsoortMap = {
        "red": "1",
        "white": "2",
        "sparkling": "3",
        "rose": "4",
        "port_red": "5",
        "port_white": "6"
    };
    if (wijnsoortMap[ovData.wine_type]) {
        document.getElementById('id_wijnsoort').value = wijnsoortMap[ovData.wine_type];
    }

    // Wijndruivensoorten selecteren
    const druivenSelect = document.getElementById('id_wijnDruivensoorten');
    const druifOpties = Array.from(druivenSelect.options);
    druifOpties.forEach(option => option.selected = false);

    ovData.grape_varieties.forEach(druif => {
        const match = druifOpties.find(opt => opt.textContent.trim().toLowerCase() === druif.toLowerCase());
        if (match) {
            match.selected = true;
        }
    });
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
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        populateForm(data.message);
        document.getElementById('ai_result').textContent = data.message;
                
        })
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(() => {
        if (btnSearch) {
            btnSearch.disabled = false;
            btnSearch.textContent = "Zoeken";
        }
        
    });
}

