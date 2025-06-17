// Dashboard functionality
const API_BASE = 'http://localhost:8000';
let autoRefreshInterval = null;
let priceChart = null;
let currentEventData = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeChart();
    refreshDashboard();
});

// Initialize price history chart
function initializeChart() {
    const ctx = document.getElementById('priceChart').getContext('2d');
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(0);
                        }
                    }
                },
                x: {
                    display: true
                }
            }
        }
    });
}

// Refresh dashboard data
async function refreshDashboard() {
    try {
        // Update last check time
        document.getElementById('lastCheck').textContent = new Date().toLocaleTimeString();
        
        // Fetch events
        const eventsResponse = await fetch(`${API_BASE}/events`);
        const events = await eventsResponse.json();
        document.getElementById('activeEvents').textContent = events.length;
        
        // Fetch price drops
        const dropsResponse = await fetch(`${API_BASE}/price-drops?hours=24`);
        const drops = await dropsResponse.json();
        document.getElementById('priceDrops').textContent = drops.length;
        
        // Update price drops list
        updatePriceDropsList(drops);
        
        // Update monitored events
        updateMonitoredEvents(events);
        
        // Find lowest price from recent data
        if (drops.length > 0) {
            const lowestDrop = Math.min(...drops.map(d => d.new_price));
            document.getElementById('lowestPrice').textContent = `$${lowestDrop.toFixed(2)}`;
        }
        
    } catch (error) {
        console.error('Error refreshing dashboard:', error);
    }
}

// Check event prices
function checkEvent() {
    document.getElementById('eventModal').classList.remove('hidden');
    document.getElementById('eventModal').classList.add('flex');
}

// Close modal
function closeModal() {
    document.getElementById('eventModal').classList.add('hidden');
    document.getElementById('eventModal').classList.remove('flex');
    document.getElementById('eventUrl').value = '';
}

// Submit event for checking
async function submitEvent() {
    const url = document.getElementById('eventUrl').value;
    if (!url) {
        alert('Please enter a URL');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/axs/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });
        
        if (response.ok) {
            const data = await response.json();
            currentEventData = data;
            updateCurrentPrices(data);
            closeModal();
            
            // Start monitoring if tickets found
            if (data.tickets && data.tickets.length > 0) {
                alert(`Found ${data.tickets.length} ticket options! Monitoring started.`);
            }
        } else {
            alert('Error checking event. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to check event. Make sure the API is running.');
    }
}

// Update current prices display
function updateCurrentPrices(data) {
    const container = document.getElementById('currentPrices');
    
    if (!data.tickets || data.tickets.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No tickets available</p>';
        return;
    }
    
    // Sort by price
    const sortedTickets = [...data.tickets].sort((a, b) => a.price - b.price);
    
    container.innerHTML = sortedTickets.map(ticket => `
        <div class="flex justify-between items-center p-3 bg-gray-50 rounded">
            <div>
                <span class="font-semibold">${ticket.section}</span>
                ${ticket.row ? `<span class="text-sm text-gray-600"> - Row ${ticket.row}</span>` : ''}
            </div>
            <div class="text-right">
                <span class="font-bold text-lg">$${ticket.price.toFixed(2)}</span>
                <span class="text-sm ${ticket.available ? 'text-green-600' : 'text-red-600'} block">
                    ${ticket.available ? 'Available' : 'Sold Out'}
                </span>
            </div>
        </div>
    `).join('');
    
    // Update chart with new data
    updatePriceChart(data);
}

// Update price history chart
function updatePriceChart(data) {
    if (!data.tickets || data.tickets.length === 0) return;
    
    // Group by section
    const sections = {};
    data.tickets.forEach(ticket => {
        if (!sections[ticket.section]) {
            sections[ticket.section] = [];
        }
        sections[ticket.section].push(ticket.price);
    });
    
    // Create datasets for chart
    const datasets = Object.keys(sections).map((section, index) => ({
        label: section,
        data: sections[section],
        borderColor: `hsl(${index * 60}, 70%, 50%)`,
        backgroundColor: `hsla(${index * 60}, 70%, 50%, 0.1)`,
        tension: 0.1
    }));
    
    // Update chart
    priceChart.data.labels = sections[Object.keys(sections)[0]].map((_, i) => `Check ${i + 1}`);
    priceChart.data.datasets = datasets;
    priceChart.update();
}

// Update price drops list
function updatePriceDropsList(drops) {
    const container = document.getElementById('priceDropsList');
    
    if (drops.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No price drops detected yet.</p>';
        return;
    }
    
    container.innerHTML = drops.map(drop => `
        <div class="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
            <div class="flex items-center space-x-4">
                <i class="fas fa-arrow-down text-green-600 text-2xl"></i>
                <div>
                    <h4 class="font-semibold">${drop.event}</h4>
                    <p class="text-sm text-gray-600">Section ${drop.section}</p>
                </div>
            </div>
            <div class="text-right">
                <p class="text-sm line-through text-gray-500">$${drop.old_price.toFixed(2)}</p>
                <p class="text-lg font-bold text-green-600">$${drop.new_price.toFixed(2)}</p>
                <p class="text-xs text-green-700">${drop.drop_percentage.toFixed(1)}% off</p>
            </div>
        </div>
    `).join('');
}

// Update monitored events list
function updateMonitoredEvents(events) {
    const container = document.getElementById('monitoredEvents');
    
    if (events.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No events being monitored.</p>';
        return;
    }
    
    container.innerHTML = events.map(event => `
        <div class="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div>
                <h4 class="font-semibold">${event.name}</h4>
                <p class="text-sm text-gray-600">${event.date}</p>
            </div>
            <button onclick="checkEventPrices('${event.name}')" 
                    class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm">
                Check Prices
            </button>
        </div>
    `).join('');
}

// Check prices for specific event
async function checkEventPrices(eventName) {
    try {
        const response = await fetch(`${API_BASE}/events/${encodeURIComponent(eventName)}/tickets`);
        const tickets = await response.json();
        
        // Format data for display
        const data = {
            event_info: { name: eventName },
            tickets: tickets
        };
        
        updateCurrentPrices(data);
    } catch (error) {
        console.error('Error checking event prices:', error);
    }
}

// Toggle auto-refresh
function toggleAutoRefresh() {
    const button = document.getElementById('autoRefreshText');
    
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        button.textContent = 'Enable Auto-Refresh';
    } else {
        autoRefreshInterval = setInterval(refreshDashboard, 30000); // Refresh every 30 seconds
        button.textContent = 'Disable Auto-Refresh';
        refreshDashboard(); // Immediate refresh
    }
}