// Function to handle comment form submission
document.querySelectorAll('form.comment-form').forEach(form => {
    form.addEventListener('submit', event => {
        event.preventDefault(); // Prevent the default form submission
        console.log("Form submitted!"); // Debugging line
        const formData = new FormData(form);

        // Send POST request to submit the new comment
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken(), // Include CSRF token for security
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Add the new comment to the comments section
                addCommentToDOM(data.comment);

                // Clear the textarea
                form.querySelector('textarea[name="content"]').value = '';
            } else {
                console.error('Failed to add the comment:', data.message);
                alert(data.message); // Show error message to user
            }
        })
        .catch(error => console.error('Error adding the comment:', error));
    });
});
// Function to add the new comment to the DOM
function addCommentToDOM(comment) {
    const commentsSection = document.getElementById('comments-section');
    const commentItem = document.createElement('div');
    commentItem.classList.add('d-flex', 'align-items-start', 'mb-4', 'comment-item');
    commentItem.style.color = 'black';
    commentItem.setAttribute('data-timestamp', comment.timestamp);

    commentItem.innerHTML = `
        <img src="/static/uploads/${comment.user_picture_path}" alt="Profile" class="rounded-circle me-3" style="width: 56px; height: 56px;">
        <div class="name-comment">
            <p class="mb-1">
                <strong>${comment.user_username}</strong>
                <small class="text-muted">${comment.relative_time}</small>
            </p>
            <p class="mb-0">${comment.content}</p>
        </div>
    `;

    // Prepend the new comment to the top of the comments section
    commentsSection.prepend(commentItem);
}

// Helper function to get CSRF token
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Sort comments if needed
function sortComments() {
    const sortValue = document.getElementById("sortBar").value;
    const commentsSection = document.getElementById("comments-section");
    const comments = Array.from(commentsSection.getElementsByClassName("comment-item"));

    // Sort comments based on the selected option
    comments.sort((a, b) => {
        const timestampA = parseFloat(a.getAttribute('data-timestamp'));
        const timestampB = parseFloat(b.getAttribute('data-timestamp'));
        
        // Sort oldest first or newest first
        return sortValue === "oldest" ? timestampA - timestampB : timestampB - timestampA;
    });

    // Clear current comments and append sorted comments
    commentsSection.innerHTML = ""; // Clear current comments
    comments.forEach(comment => commentsSection.appendChild(comment)); // Append sorted comments
}

// Initial sorting if needed
sortComments();
