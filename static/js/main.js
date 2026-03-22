const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add("show");
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.12 });

document.querySelectorAll(".product-card").forEach((card, index) => {
    card.style.transitionDelay = `${index * 60}ms`;
    observer.observe(card);
});

const orbs = document.querySelectorAll(".bg-orb");
let tick = 0;
function animateHud() {
    tick += 0.008;
    orbs.forEach((orb, i) => {
        const x = Math.sin(tick + i) * 8;
        const y = Math.cos(tick + i * 0.6) * 8;
        orb.style.transform = `translate(${x}px, ${y}px)`;
    });
    requestAnimationFrame(animateHud);
}
animateHud();
