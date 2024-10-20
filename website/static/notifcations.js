// Function to fetch new notifications and update the dropdown list
function fetchNotifications() {
    fetch('/api/notifications')  // Endpoint to get notifications as JSON
        .then(response => response.json())
        .then(data => {
            const notificationList = document.getElementById('notificationsList');
            notificationList.innerHTML = '';  // Clear the current dropdown list
            
            // Update unread count displayed in the navbar
            const unreadCountElement = document.getElementById('unreadCount');
            unreadCountElement.textContent = data.unread_count > 0 ? data.unread_count : '';

            if (data.notifications.length > 0) {
                // Limit to the top 5 notifications
                data.notifications.slice(0, 5).forEach(notification => {
                    const listItem = document.createElement('li');
                    listItem.classList.add('dropdown-item');
                    if (!notification.is_read) {
                        listItem.classList.add('text-bold');
                    }
                    listItem.innerHTML = `
                        <a href="/notifications/read/${notification.id}" class="dropdown-item" onclick="markNotificationAsRead(${notification.id})">
                            ${notification.message}
                        </a>
                    `;
                    notificationList.appendChild(listItem);
                });
            } else {
                // If there are no notifications, show a default message
                const noNotificationItem = document.createElement('li');
                noNotificationItem.classList.add('dropdown-item');
                noNotificationItem.textContent = 'You have no notifications.';
                notificationList.appendChild(noNotificationItem);
            }
        })
        .catch(error => console.error('Error fetching notifications:', error));
}

// Function to mark a specific notification as read
function markNotificationAsRead(notificationId) {
    fetch(`/api/notifications/read/${notificationId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),  // Ensure you include CSRF token if using Flask-WTF
        }
    })
    .then(response => {
        if (response.ok) {
            console.log(`Notification ${notificationId} marked as read.`);
            fetchNotifications(); // Refresh the notifications list to reflect changes
        } else {
            console.error('Failed to mark notification as read.');
        }
    })
    .catch(error => console.error('Error marking notification as read:', error));
}

// Function to mark all notifications as read when on the notifications page
function markAllAsRead() {
    fetch('/api/notifications/read/all', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),  // Ensure you include CSRF token if using Flask-WTF
        }
    })
    .then(response => {
        if (response.ok) {
            console.log('All notifications marked as read.');
            // Fetch notifications again to update the unread count
            fetchNotifications();
        } else {
            console.error('Failed to mark notifications as read.');
        }
    })
    .catch(error => console.error('Error marking notifications as read:', error));
}

// Fetch notifications initially and then every 30 seconds
fetchNotifications();
setInterval(fetchNotifications, 30000);  // Update every 30 seconds

// If on the notifications page, mark all as read
if (window.location.pathname === '/notifications') {
    markAllAsRead();
}

// Helper function to get CSRF token
function getCSRFToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    return csrfToken;
}
