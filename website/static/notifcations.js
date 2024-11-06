// Fetch notifications initially and then every 30 seconds
fetchNotifications();
setInterval(fetchNotifications, 30000);  // Update every 30 seconds

// Check for due alarms every 45 seconds
setInterval(checkDueAlarms, 45000);  // Check every 45 seconds

function fetchNotifications() {
    fetch('/api/notifications')  
    .then(response => response.json())
    .then(data => {
        console.log(data);  // Log the data to see if sponsorship_id is included
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

                // Check if sponsor_id exists and add a link with correct sponsorship_id
                const sponsorId = notification.sponsorship_id || null;
                if (sponsorId) {
                    listItem.innerHTML = `
                        <a href="/sponsor/${sponsorId}" class="dropdown-item" onclick="markNotificationAsRead(${notification.id}, ${sponsorId}); return false;">
                            ${notification.message}
                        </a>
                    `;
                } else {
                    console.log('Missing sponsor_id for notification:', notification);
                    listItem.innerHTML = `
                        <a href="#" class="dropdown-item">
                            ${notification.message}
                        </a>
                    `;
                }

                notificationList.appendChild(listItem);
            });
        } else {
            // If there are no notifications, show a default message
            const noNotificationItem = document.createElement('li');
            noNotificationItem.classList.add('dropdown-item');
            noNotificationItem.textContent = 'You have no notifications.';
            notificationList.appendChild(noNotificationItem);
        }

        // Add the customized "View All Notifications" button at the bottom of the dropdown list
        const viewAllItem = document.createElement('li');
        viewAllItem.innerHTML = `
            <a href="/notifications" class="view-all-notifications" style="color:#012CB8; text-decoration: none; width: 100%; padding: 5px; display: block; text-align: center;">
                View All Notifications
            </a>
        `;
        notificationList.appendChild(viewAllItem);
    })
    .catch(error => console.error('Error fetching notifications:', error));
}

// Listen for when the dropdown is shown and mark all notifications as read
document.getElementById('notificationsDropdown').addEventListener('click', () => {
    markAllAsRead();
    fetchNotifications(); // Fetch notifications to update the dropdown list
});

// Function to mark all notifications as read
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
        } else if (response.status === 204) {
            console.log('No unread notifications to mark as read.');
        } else {
            console.error('Failed to mark notifications as read.');
        }
    })
    .catch(error => console.error('Error marking notifications as read:', error));
}

// Function to get CSRF token
function getCSRFToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    return csrfToken;
}

// Function to mark a notification as read and handle the redirect
function markNotificationAsRead(notificationId, sponsorId) {
    console.log('Notification ID:', notificationId); // Check if notificationId is passed correctly
    console.log('Sponsor ID:', sponsorId); // Check if sponsorId is passed correctly

    // Redirect to the corresponding sponsorship page
    if (sponsorId) {
        window.location.href = `/sponsor/${sponsorId}`; // Adjust to your route
    } else {
        console.error('No Sponsor ID found for this notification');
    }

    // You may want to mark the notification as read here (e.g., by sending a request to an API)
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
        } else {
            console.error(`Failed to mark notification ${notificationId} as read.`);
        }
    })
    .catch(error => console.error('Error marking notification as read:', error));
}

// Initialize Socket.IO for real-time notifications
const socket = io('/notifications');

// Listen for real-time alarm notifications
socket.on('alarm_notification', function(data) {
    const notificationMessage = `${data.message}`;
    
    // Create a new notification entry
    const newNotification = {
        id: Date.now(), // Use a timestamp as a unique ID for the demo
        message: notificationMessage,
        is_read: false
    };

    // Add the new notification to the notification list
    const notificationList = document.getElementById('notificationsList');
    const listItem = document.createElement('li');
    listItem.classList.add('dropdown-item', 'text-bold');
    listItem.innerHTML = `
        <a href="#" class="dropdown-item" onclick="markNotificationAsRead(${newNotification.id}, null); return false;">
            ${notificationMessage}
        </a>
    `;
    notificationList.prepend(listItem); // Add to the top of the list

    // Update unread count displayed in the navbar
    const unreadCountElement = document.getElementById('unreadCount');
    const currentCount = parseInt(unreadCountElement.textContent) || 0;
    unreadCountElement.textContent = currentCount + 1; // Increment unread count
});

// Function to check for due alarms and notify
function checkDueAlarms() {
    fetch('/api/due_alarms')  // Endpoint to check for due alarms
        .then(response => response.json())
        .then(data => {
            if (data.alarms.length > 0) {
                data.alarms.forEach(alarm => {
                    const notificationMessage = `${alarm.message}`;
                    
                    // Create a new notification entry
                    const newNotification = {
                        id: Date.now(), // Use a timestamp as a unique ID for the demo
                        message: notificationMessage,
                        is_read: false
                    };

                    // Add the new notification to the notification list
                    const notificationList = document.getElementById('notificationsList');
                    const listItem = document.createElement('li');
                    listItem.classList.add('dropdown-item', 'text-bold');
                    listItem.innerHTML = `
                        <a href="#" class="dropdown-item" onclick="markNotificationAsRead(${newNotification.id}); return false;">
                            ${notificationMessage}
                        </a>
                    `;
                    notificationList.prepend(listItem); // Add to the top of the list

                    // Update unread count displayed in the navbar
                    const unreadCountElement = document.getElementById('unreadCount');
                    const currentCount = parseInt(unreadCountElement.textContent) || 0;
                    unreadCountElement.textContent = currentCount + 1; // Increment unread count
                });
            }
        })
        .catch(error => console.error('Error checking due alarms:', error));
}
