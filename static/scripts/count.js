function updateUnreadCount() {
    fetch('/notifications/unread-count/')
        .then(res => res.json())
        .then(data => {
            document.querySelectorAll('.notif-badge').forEach(badge => {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.classList.remove('hidden');
                } else {
                    badge.classList.add('hidden');
                }
            });
        });
}


function showOrderItemsCount() {
    fetch('/order-items/count/')
        .then(res => res.json())
        .then(data => {
            document.querySelectorAll('.order-item-badge').forEach(badge => {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.classList.remove('hidden');
                } else {
                    badge.textContent = '';
                    badge.classList.add('hidden');
                }
            });
        });
}



document.addEventListener('DOMContentLoaded', function () {
    updateUnreadCount();
    showOrderItemsCount();
});
