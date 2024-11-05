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
                        <a href="#" class="dropdown-item" onclick="markNotificationAsRead(${notification.id}); return false;">
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

// Listen for when the dropdown is shown and mark all notifications as read
document.getElementById('notificationsDropdown').addEventListener('click', () => {
    markAllAsRead();
    fetchNotifications(); // Fetch notifications to update the dropdown list
});


// Function to check for due alarms and notify
function checkDueAlarms() {
    fetch('/api/due_alarms')  // Endpoint to check for due alarms
        .then(response => response.json())
        .then(data => {
            if (data.alarms.length > 0) {
                data.alarms.forEach(alarm => {
                    const notificationMessage = `Alarm notification: ${alarm.message}`;
                    
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

// Fetch notifications initially and then every 30 seconds
fetchNotifications();
setInterval(fetchNotifications, 30000);  // Update every 30 seconds

// Check for due alarms every minute
setInterval(checkDueAlarms, 45000);  // Check every 45 seconds

// If on the notifications page, mark all as read
if (window.location.pathname === '/notifications') {
    markAllAsRead();
}

// Helper function to get CSRF token
function getCSRFToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    return csrfToken;
}

// Initialize Socket.IO for real-time notifications
const socket = io('/notifications');

// Listen for real-time alarm notifications
socket.on('alarm_notification', function(data) {
    const notificationMessage = `Alarm notification: ${data.message}`;
    
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

// Function to fetch new notifications and update the dropdown list
function fetchNotifications() {
    fetch('/notifications/latest')  // Update to match the defined route
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const notificationList = document.getElementById('notificationsList');
            notificationList.innerHTML = '';  // Clear the current dropdown list

            // Update unread count displayed in the navbar
            const unreadCountElement = document.getElementById('unreadCount');
            unreadCountElement.textContent = data.filter(n => !n.is_read).length || '';

            if (data.length > 0) {
                // Limit to the top 5 notifications
                data.forEach(notification => {
                    const listItem = document.createElement('li');
                    listItem.classList.add('dropdown-item');
                    if (!notification.is_read) {
                        listItem.classList.add('text-bold');
                    }
                    listItem.innerHTML = `
                        <a href="#" class="dropdown-item" onclick="markNotificationAsRead(${notification.id}); return false;">
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

            // Add a button to view all notifications
            const viewAllButton = document.createElement('button');
            viewAllButton.classList.add('dropdown-item', 'text-center');
            viewAllButton.textContent = 'View All Notifications';
            viewAllButton.onclick = function() {
                window.location.href = '/notifications'; // Redirect to the notifications page
            };
            notificationList.appendChild(viewAllButton);
        })
        .catch(error => console.error('Error fetching notifications:', error));
}

// Function to redirect to the corresponding sponsorship page
function markNotificationAsRead(sponsorshipId) {
    // Redirect to the corresponding sponsorship page
    window.location.href = `/sponsor/${sponsorshipId}`; // Adjust to your route
}
