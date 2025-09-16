// Enhanced Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Animate stat numbers on load
    animateStatNumbers();
    
    // Add real-time clock
    updateClock();
    setInterval(updateClock, 1000);
    
    // Add hover effects to interactive elements
    addHoverEffects();
    
    // Auto-refresh data every 5 minutes
    setInterval(refreshDashboardData, 300000);
    
    // Add keyboard navigation
    addKeyboardNavigation();
});

function animateStatNumbers() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(element => {
        const finalValue = parseInt(element.textContent);
        let currentValue = 0;
        const increment = finalValue / 50; // Animate over 50 steps
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                element.textContent = finalValue;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(currentValue);
            }
        }, 30);
    });
}

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-IN', {
        hour12: true,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    // Add clock to dashboard header if it doesn't exist
    let clockElement = document.getElementById('dashboard-clock');
    if (!clockElement) {
        clockElement = document.createElement('div');
        clockElement.id = 'dashboard-clock';
        clockElement.style.cssText = `
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 8px 12px;
            border-radius: 8px;
            font-weight: 600;
            color: #333;
            font-size: 0.9rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        `;
        
        const header = document.querySelector('.dashboard-header');
        if (header) {
            header.style.position = 'relative';
            header.appendChild(clockElement);
        }
    }
    
    clockElement.textContent = timeString;
}

function addHoverEffects() {
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.action-btn, .view-btn, .quick-action-btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

function refreshDashboardData() {
    // Add a subtle loading indicator
    const header = document.querySelector('.dashboard-header');
    const loader = document.createElement('div');
    loader.innerHTML = '🔄 Refreshing...';
    loader.style.cssText = `
        position: absolute;
        bottom: 10px;
        right: 20px;
        font-size: 0.8rem;
        color: #666;
        opacity: 0.7;
    `;
    
    header.appendChild(loader);
    
    // Simulate data refresh (in a real app, this would be an AJAX call)
    setTimeout(() => {
        loader.remove();
        // You could reload specific sections here
        // location.reload(); // Full page reload as fallback
    }, 2000);
}

function addKeyboardNavigation() {
    document.addEventListener('keydown', function(e) {
        // Quick actions with keyboard shortcuts
        if (e.altKey) {
            switch(e.key) {
                case 'q': // Alt+Q for Quick Check-in
                    e.preventDefault();
                    const quickCheckinBtn = document.querySelector('a[href*="quick-checkin"]');
                    if (quickCheckinBtn) quickCheckinBtn.click();
                    break;
                case 'n': // Alt+N for New Check-in
                    e.preventDefault();
                    const newCheckinBtn = document.querySelector('a[href*="checkin-create"]');
                    if (newCheckinBtn) newCheckinBtn.click();
                    break;
                case 'l': // Alt+L for List all check-ins
                    e.preventDefault();
                    const listBtn = document.querySelector('a[href*="checkin-list"]');
                    if (listBtn) listBtn.click();
                    break;
            }
        }
    });
    
    // Add keyboard shortcut hints
    const shortcuts = document.createElement('div');
    shortcuts.innerHTML = `
        <div style="position: fixed; bottom: 20px; left: 20px; background: rgba(0,0,0,0.8); color: white; padding: 10px; border-radius: 8px; font-size: 0.8rem; opacity: 0; transition: opacity 0.3s;" id="keyboard-hints">
            <div><strong>Keyboard Shortcuts:</strong></div>
            <div>Alt+Q: Quick Check-in</div>
            <div>Alt+N: New Check-in</div>
            <div>Alt+L: List Check-ins</div>
        </div>
    `;
    document.body.appendChild(shortcuts);
    
    // Show shortcuts on Alt key press
    document.addEventListener('keydown', function(e) {
        if (e.altKey) {
            document.getElementById('keyboard-hints').style.opacity = '1';
        }
    });
    
    document.addEventListener('keyup', function(e) {
        if (!e.altKey) {
            document.getElementById('keyboard-hints').style.opacity = '0';
        }
    });
}

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);