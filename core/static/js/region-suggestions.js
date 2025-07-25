const regionInput = document.getElementById('region-input');
const container = document.createElement('div');
container.classList.add('autocomplete-suggestions');
regionInput.parentNode.appendChild(container);

regionInput.addEventListener('input', function () {
const query = this.value;

if (query.length < 2) {
    container.innerHTML = '';
    return;
}

fetch(`/ajax/region-suggestions/?q=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(data => {
    container.innerHTML = '';
    data.forEach(region => {
        const item = document.createElement('div');
        item.classList.add('autocomplete-suggestion');
        item.textContent = region;
        item.addEventListener('click', () => {
        regionInput.value = region;
        container.innerHTML = '';
        });
        container.appendChild(item);
    });
    });
});

document.addEventListener('click', function (e) {
if (!container.contains(e.target) && e.target !== regionInput) {
    container.innerHTML = '';
}
});