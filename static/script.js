/* script.js */

// JavaScript para funcionalidades interativas

// Adiciona uma classe ao cabeçalho quando a página é rolada
window.addEventListener('scroll', function() {
    var header = document.querySelector('header');
    header.classList.toggle('sticky', window.scrollY > 0);
});
