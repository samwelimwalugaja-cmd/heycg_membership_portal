// Notification system
class NotificationSystem {
  constructor() {
    this.bell = document.getElementById('notificationBell');
    this.dropdown = document.getElementById('notificationDropdown');
    this.list = document.getElementById('notificationList');
    this.badge = document.getElementById('notificationBadge');
    this.pollInterval = null;
    this.init();
  }
  
  init() {
    this.loadNotifications();
    this.startPolling();
    this.setupEventListeners();
  }
  
  loadNotifications() {
    fetch('/members/api/notifications/')
      .then(response => response.json())
      .then(data => {
        this.updateUI(data);
      })
      .catch(error => console.error('Error loading notifications:', error));
  }
  
  updateUI(data) {
    // Update badge
    if (data.unread_count > 0) {
      this.badge.textContent = data.unread_count > 9 ? '9+' : data.unread_count;
      this.badge.style.display = 'inline';
    } else {
      this.badge.style.display = 'none';
    }
    
    // Update list
    if (data.notifications.length === 0) {
      this.list.innerHTML = `
        <div class="dropdown-item text-center text-muted py-3">
          <i class="bi bi-bell-slash"></i> No new notifications
        </div>
      `;
      return;
    }
    
    let html = '';
    data.notifications.forEach(notif => {
      const icon = this.getIcon(notif.type);
      const readClass = notif.is_read ? '' : 'fw-bold';
      html += `
        <a href="${notif.link || '#'}" class="dropdown-item notification-item ${notif.is_read ? '' : 'unread'}" 
           data-id="${notif.id}" style="border-left: 3px solid ${notif.is_read ? 'transparent' : '#0a58ca'}">
          <div class="d-flex gap-2 align-items-start">
            <span class="mt-1">${icon}</span>
            <div class="flex-grow-1">
              <div class="d-flex justify-content-between">
                <span class="${readClass}">${notif.title}</span>
                <small class="text-muted">${notif.time_ago}</small>
              </div>
              <div class="small text-muted">${notif.message}</div>
            </div>
          </div>
        </a>
      `;
    });
    
    this.list.innerHTML = html;
  }
  
  getIcon(type) {
    const icons = {
      'payment': '<i class="bi bi-credit-card text-primary"></i>',
      'membership': '<i class="bi bi-person-check text-warning"></i>',
      'donation': '<i class="bi bi-heart text-danger"></i>',
      'announcement': '<i class="bi bi-megaphone text-info"></i>'
    };
    return icons[type] || '<i class="bi bi-bell text-secondary"></i>';
  }
  
  startPolling() {
    // Poll every 30 seconds
    this.pollInterval = setInterval(() => {
      this.loadNotifications();
    }, 30000);
  }
  
  setupEventListeners() {
    // Refresh on dropdown open
    this.bell?.addEventListener('click', () => {
      this.loadNotifications();
    });
    
    // Mark as read on click
    this.list?.addEventListener('click', (e) => {
      const item = e.target.closest('.notification-item');
      if (item && item.dataset.id) {
        this.markAsRead(item.dataset.id);
      }
    });
  }
  
  markAsRead(id) {
    fetch(`/members/notifications/mark/${id}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': this.getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        this.loadNotifications();
      }
    });
  }
  
  getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new NotificationSystem();
});