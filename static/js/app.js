/* RAG Chatbot - JavaScript Utilities */
const Utils = {
    formatDate(date) {
        return new Date(date).toLocaleDateString('id-ID', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    },
    notify(message, type = 'info') {
        const container = document.getElementById('notifications') || this.createNotificationContainer();
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        container.appendChild(notification);
        setTimeout(() => { notification.classList.add('fade-out'); setTimeout(() => notification.remove(), 300); }, 3000);
    },
    createNotificationContainer() {
        const container = document.createElement('div');
        container.id = 'notifications';
        container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 1000; display: flex; flex-direction: column; gap: 10px;';
        document.body.appendChild(container);
        return container;
    }
};
document.body.addEventListener('htmx:afterRequest', function(event) { if (event.detail.failed) { Utils.notify('Terjadi kesalahan', 'error'); } });
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => { textarea.addEventListener('input', function() { this.style.height = 'auto'; this.style.height = this.scrollHeight + 'px'; }); });
});
window.Utils = Utils;
