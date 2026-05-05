
document.addEventListener('DOMContentLoaded', function() {
    const fotoInput = document.getElementById('id_foto');
    if (fotoInput) {
        fotoInput.onchange = function () {
            var src = URL.createObjectURL(this.files[0]);
            document.getElementById('image').src = src;
            document.getElementById('btnSearch').hidden = false;
            document.getElementById('ai_result').hidden = false;
        };
    }

    const druivenEl = document.getElementById('id_wijnDruivensoorten');
    if (druivenEl && typeof TomSelect !== 'undefined') {
        window.druivenTomSelect = new TomSelect(druivenEl, {
            plugins: ['remove_button'],
            dropdownParent: 'body',
            create: function (input, callback) {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                fetch('/druivensoort/ajax-create/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken,
                    },
                    body: 'omschrijving=' + encodeURIComponent(input),
                })
                .then(r => r.json())
                .then(data => {
                    if (data.id) callback({ value: String(data.id), text: data.omschrijving });
                    else callback();
                })
                .catch(() => callback());
            },
            createFilter: input => input.trim().length > 1,
        });
    }
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

    // Wijnsoort select
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

    // Druivensoorten via Tom Select
    const ts = window.druivenTomSelect;
    if (ts) {
        ts.clear(true);
        const unmatched = [];
        (ovData.grape_varieties || []).forEach(druif => {
            const matchKey = Object.keys(ts.options).find(
                k => ts.options[k].text.trim().toLowerCase() === druif.toLowerCase()
            );
            if (matchKey) {
                ts.addItem(matchKey, true);
            } else {
                unmatched.push(druif);
            }
        });
        ts.trigger('change');
        showUnmatchedGrapes(unmatched, ts);
    }

    const firstField = document.getElementById('id_domein');
    if (firstField) firstField.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showUnmatchedGrapes(unmatched, ts) {
    const existing = document.getElementById('grape-warnings');
    if (existing) existing.remove();
    if (!unmatched.length) return;

    const container = document.createElement('div');
    container.id = 'grape-warnings';
    container.className = 'grape-warnings';

    unmatched.forEach(druif => {
        const allOptions = Object.values(ts.options);
        const d = druif.toLowerCase();
        const suggestions = allOptions.filter(o =>
            o.text.toLowerCase().includes(d) || d.includes(o.text.toLowerCase())
        );

        const row = document.createElement('div');
        row.className = 'grape-warning-row';

        let chips = '';
        suggestions.forEach(s => {
            chips += `<button type="button" class="grape-chip" data-value="${s.value}">${s.text}</button> `;
        });

        row.innerHTML = `
            <span class="grape-name">AI: <em>${druif}</em></span>
            ${chips ? `<span class="grape-suggestions">Bedoeld? ${chips}</span>` : ''}
            <button type="button" class="grape-add" data-naam="${druif}">+ Toevoegen</button>
            <button type="button" class="grape-ignore">Negeer</button>`;

        row.querySelectorAll('.grape-chip').forEach(btn => {
            btn.addEventListener('click', () => {
                ts.addItem(btn.dataset.value);
                row.remove();
                if (!container.children.length) container.remove();
            });
        });

        row.querySelector('.grape-add').addEventListener('click', () => {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            fetch('/druivensoort/ajax-create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                },
                body: 'omschrijving=' + encodeURIComponent(druif),
            })
            .then(r => r.json())
            .then(data => {
                if (data.id) {
                    ts.addOption({ value: String(data.id), text: data.omschrijving });
                    ts.addItem(String(data.id));
                    row.remove();
                    if (!container.children.length) container.remove();
                }
            });
        });

        row.querySelector('.grape-ignore').addEventListener('click', () => {
            row.remove();
            if (!container.children.length) container.remove();
        });

        container.appendChild(row);
    });

    const tsEl = document.getElementById('id_wijnDruivensoorten');
    const tsWrapper = tsEl.closest('.ts-wrapper') || tsEl;
    tsWrapper.insertAdjacentElement('afterend', container);
}

function callPythonFunction() {
    const baseUrl = `${window.location.protocol}//${window.location.host}`;
    const fileInput = document.getElementById('id_foto');
    const imageFile = fileInput.files[0];
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
    formData.append('image', imageFile);

    fetch(baseUrl + '/AI-zoeken/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(async response => {
        if (!response.ok) {
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
