function updateUnreadCount() {
    fetch('/notifications/unread-count/')
        .then(res => res.json())
        .then(data => {
            const badge = document.querySelector('.notif-badge');
            if (badge) {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.classList.remove('hidden');
                } else {
                    badge.classList.add('hidden');
                }
            }
        });
}

document.addEventListener('DOMContentLoaded', function () {
    updateUnreadCount();
});
