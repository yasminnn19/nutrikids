// Form submission
document.addEventListener('DOMContentLoaded', function() {
    const topicForm = document.getElementById('topic-form');
    if (topicForm) {
        topicForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values
            const title = document.getElementById('topic-title').value;
            const category = document.getElementById('topic-category').value;
            const content = document.getElementById('topic-content').value;
            
            // Here you would typically send the data to your server
            // For now, we'll just show an alert and reset the form
            alert(`Tópico "${title}" criado com sucesso na categoria ${category}!`);
            this.reset();
            
            // Scroll to top to see the new topic
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Simulate category filtering
    document.querySelectorAll('.category-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            document.querySelectorAll('.category-link').forEach(item => {
                item.classList.remove('active');
            });
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Here you would typically filter the topics by category
            // For now, we'll just show an alert
            alert(`Filtrando tópicos por: ${this.textContent}`);
        });
    });
});