var btn = document.querySelector('#copy');
var link = document.querySelector('#link');


btn.addEventListener('click', copy);
function copy(){
    event.preventDefault();
    link.select();
    link.setSelectionRange(0, 99999);
    navigator.clipboard.writeText
                (link.value);
}
