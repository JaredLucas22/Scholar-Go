// Function to handle follow/unfollow button click
document.querySelectorAll('.follow-button').forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default button behavior

        const sponsorshipId = this.dataset.sponsorshipId;
        const isFollowing = this.dataset.isFollowing === 'true';

        if (!sponsorshipId) {
            console.error('Sponsorship ID is not defined.');
            return;
        }

        // Send the POST request to the server
        fetch(`/follow/${sponsorshipId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf_token'), // Include CSRF token for security
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Toggle the isFollowing state
                this.dataset.isFollowing = (!isFollowing).toString();

                const icon = this.querySelector('i');
                if (data.is_following) {  // Change 'is_liked' to 'is_following'
                    icon.classList.remove('far', 'fa-bookmark');  // Change 'far' class for following state
                    icon.classList.add('fas', 'fa-bookmark');      // Add 'fas' class for followed state
                } else {
                    icon.classList.remove('fas', 'fa-bookmark');  // Remove 'fas' class for unfollowed state
                    icon.classList.add('far', 'fa-bookmark');      // Add 'far' class for unfollowed state
                }
                

            } else {
                console.error('Failed to follow/unfollow:', data.message);
            }
        })
        .catch(error => {
            console.error('Error following/unfollowing:', error);
        });
    });
});

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
