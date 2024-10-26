let currentIndex = 0;
const items = document.querySelectorAll('.carousel-item');
const totalItems = items.length;

function showNextItem() {
    currentIndex = (currentIndex + 1) % totalItems; // Vai para o próximo item, e volta para o primeiro ao final
    const carousel = document.querySelector('.carousel');
    const newTransformValue = -currentIndex * 100;
    carousel.style.transform = `translateX(${newTransformValue}%)`;
}

// Define um intervalo para alternar automaticamente entre os produtos a cada 3 segundos
setInterval(showNextItem, 3000);