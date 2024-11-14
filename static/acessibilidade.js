// acessibilidade.js

// Função para alternar contraste
function toggleContrast() {
    document.body.classList.toggle('high-contrast');
}

// Funções para aumentar e diminuir o tamanho do texto
let currentTextSize = 1; // Tamanho padrão (1x)

function increaseTextSize() {
    currentTextSize += 0.2; // Aumenta o tamanho do texto
    document.body.style.fontSize = currentTextSize + 'em'; // Define o novo tamanho
}

function decreaseTextSize() {
    if (currentTextSize > 0.6) { // Limite inferior
        currentTextSize -= 0.2; // Diminui o tamanho do texto
        document.body.style.fontSize = currentTextSize + 'em'; // Define o novo tamanho
    }
}

function resetTextSize() {
    currentTextSize = 1; // Reseta o tamanho do texto
    document.body.style.fontSize = currentTextSize + 'em'; // Redefine o tamanho para padrão
}

// Adicionando eventos de clique aos botões
document.getElementById('toggleContrastButton').addEventListener('click', toggleContrast);
document.getElementById('increaseTextSizeButton').addEventListener('click', increaseTextSize);
document.getElementById('decreaseTextSizeButton').addEventListener('click', decreaseTextSize);
document.getElementById('resetTextSizeButton').addEventListener('click', resetTextSize); // Adicionando o evento para o botão de reset
