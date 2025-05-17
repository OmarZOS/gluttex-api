document.addEventListener('DOMContentLoaded', function() {
  // Auto-animate cards on load
  const cards = document.querySelectorAll('.language-card');
  
  // Add ripple effect to buttons
  cards.forEach(card => {
    card.addEventListener('click', function(e) {
      // Add temporary active state
      this.classList.add('active');
      setTimeout(() => this.classList.remove('active'), 300);
      
      // Optional: Save language preference
      localStorage.setItem('preferredLang', this.dataset.lang);
    });
  });
  
  // Check for preferred language
  const preferredLang = localStorage.getItem('preferredLang');
  if (preferredLang) {
    const preferredCard = document.querySelector(`.language-card[data-lang="${preferredLang}"]`);
    if (preferredCard) {
      preferredCard.style.transform = 'scale(1.05)';
      preferredCard.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
    }
  }
  
  // Background animation
  const bgAnimation = document.querySelector('.background-animation');
  if (bgAnimation) {
    document.addEventListener('mousemove', (e) => {
      const x = e.clientX / window.innerWidth;
      const y = e.clientY / window.innerHeight;
      bgAnimation.style.backgroundPosition = `${x * 30}px ${y * 30}px`;
    });
  }
});