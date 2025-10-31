// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// // Newsletter form submission
// document.querySelector('form')?.addEventListener('submit', function(e) {
//     e.preventDefault();
//     const email = this.querySelector('input[type="email"]').value;
    
//     // Here you would typically send the email to your server
//     // For now, we'll just show an alert
//     alert(`Obrigado por assinar nossa newsletter! Você receberá nossas receitas em ${email}`);
//     this.querySelector('input[type="email"]').value = '';
// });