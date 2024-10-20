// Function to handle like/unlike button click
document.querySelectorAll('.like-button').forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default button behavior

        const sponsorshipId = this.dataset.sponsorshipId;
        const isFollowing = this.dataset.isFollowing === 'true';

        if (!sponsorshipId) {
            console.error('Sponsorship ID is not defined.');
            return;
        }

        // Send the POST request to the server
        fetch(`/like/${sponsorshipId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf_token') // Include CSRF token for security
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the button state based on the response
                const icon = button.querySelector('i');
                if (data.is_liked) {
                    icon.classList.remove('far');
                    icon.classList.add('fas', 'liked');
                } else {
                    icon.classList.remove('fas', 'liked');
                    icon.classList.add('far');
                }

                // Get the likes count element and the deadline
                const likesCountElement = document.getElementById('likes-count'); // Use the correct ID

                if (likesCountElement) {
                    const deadline = likesCountElement.dataset.deadline; // Get the deadline from the data attribute
                    likesCountElement.textContent = `Likes: ${data.likes_count} | Deadline on ${deadline}`;
                }

                // Show a flash message
                showFlashMessage(data.message);
            } else {
                console.error('Failed to like/unlike:', data.message);
            }
        })
        .catch(error => {
            console.error('Error liking/unliking:', error);
        });        
    });
});
