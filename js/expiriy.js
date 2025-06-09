let products = [];

// Fetch expiry data from Flask backend
async function fetchExpiryAlerts() {
    try {
        const response = await fetch('/expiry_alerts');
        const data = await response.json();

        if (data.error) {
            console.error('Backend error:', data.error);
            return;
        }

        products = data;
        displayProducts(products);
    } catch (err) {
        console.error('Fetch error:', err);
    }
}

// Function to get expiry warning class
function getExpiryWarningClass(daysUntilExpiry) {
    if (daysUntilExpiry <= 1) return 'warning-day';
    if (daysUntilExpiry <= 7) return 'warning-week';
    if (daysUntilExpiry <= 30) return 'warning-month';
    if (daysUntilExpiry <= 60) return 'warning-caution';
    if (daysUntilExpiry <= 90) return 'warning-watch';
    if (daysUntilExpiry <= 180) return 'warning-attention';
    return 'warning-safe';
}

// Function to create product card
function createProductCard(product) {
    const warningClass = getExpiryWarningClass(product.time_to_expiry);

    return `
        <div class="product-card">
            <img src="/pictures/product1.jpg" alt="${product.product_name}" onerror="this.src='https://placehold.co/300x200'">
            <div class="product-info">
                <h3>${product.product_name}</h3>
                <p>Expiry Date: ${new Date(product.expiry_date).toLocaleDateString()}</p>
                <p>Demand: ${product.demand}</p>
                <div class="expiry-warning ${warningClass}">
                    ${product.expiry_alert} — Expires in ${product.time_to_expiry} days
                </div>
            </div>
        </div>
    `;
}

// Function to display filtered products
function displayProducts(productsToShow) {
    const container = document.getElementById('productsContainer');
    container.innerHTML = productsToShow.map(product => createProductCard(product)).join('');
}

// Function to filter products
function filterProducts() {
    const timeFilter = document.getElementById('timeFilter').value;
    const searchText = document.getElementById('searchProduct').value.toLowerCase();

    const filteredProducts = products.filter(product => {
        const daysUntilExpiry = product.time_to_expiry;
        const matchesSearch =
            product.product_name.toLowerCase().includes(searchText) ||
            product.demand.toLowerCase().includes(searchText);

        switch (timeFilter) {
            case 'day':
                return daysUntilExpiry <= 1 && matchesSearch;
            case 'week':
                return daysUntilExpiry <= 7 && matchesSearch;
            case 'month':
                return daysUntilExpiry <= 30 && matchesSearch;
            default:
                return matchesSearch;
        }
    });

    displayProducts(filteredProducts);
}

// Event listeners
document.getElementById('timeFilter').addEventListener('change', filterProducts);
document.getElementById('searchProduct').addEventListener('input', filterProducts);

// Initial load
window.addEventListener('DOMContentLoaded', fetchExpiryAlerts);