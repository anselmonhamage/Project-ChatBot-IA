let currentIndex = 0;
const items = document.querySelectorAll('.carousel-item');
const totalItems = items.length;

function showNextItem() {
    currentIndex = (currentIndex + 1) % totalItems;
    const carousel = document.querySelector('.carousel');
    const newTransformValue = -currentIndex * 100;
    carousel.style.transform = `translateX(${newTransformValue}%)`;
}

setInterval(showNextItem, 3000);