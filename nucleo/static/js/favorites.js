document.addEventListener('DOMContentLoaded', function() {
    // Add click event to all favorite icons
    const favoriteIcons = document.querySelectorAll('.favorite-icon');
    
    favoriteIcons.forEach(icon => {
        icon.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle the favorite state
            this.classList.toggle('favorited');
            
            // Change the heart color
            const heart = this.querySelector('.heart') || this;
            if (this.classList.contains('favorited')) {
                heart.style.color = '#ff6b6b';
                // Here you would typically send a request to save the favorite
                console.log('Product added to favorites');
            } else {
                heart.style.color = '#ccc';
                // Here you would typically send a request to remove the favorite
                console.log('Product removed from favorites');
            }
        });
    });
});