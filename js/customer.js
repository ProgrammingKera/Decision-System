let products = [];
let cart = [];

document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
    document.getElementById("paidAmount").addEventListener("input", updateBillingSummary);
});

function fetchProducts() {
    fetch("/api/products")
        .then(res => res.json())
        .then(data => {
            products = data;
            displayProducts(products);
        })
        .catch(err => console.error("Error loading products:", err));
}

document.getElementById("categorySelect").addEventListener("change", applyFilters);
document.getElementById("searchInput").addEventListener("input", applyFilters);

function applyFilters() {
    const category = document.getElementById("categorySelect").value;
    const searchTerm = document.getElementById("searchInput").value.toLowerCase();

    const filtered = products.filter(product => {
        const matchCategory = category === "All Categories" || product.category === category;
        const matchSearch = product.product_name.toLowerCase().includes(searchTerm) || 
                            (product.product_code && product.product_code.toLowerCase().includes(searchTerm));
        return matchCategory && matchSearch;
    });

    displayProducts(filtered);
}


function displayProducts(products) {
    const container = document.getElementById("productContainer");
    container.innerHTML = "";

    products.forEach(product => {
        const card = document.createElement("div");
        card.className = "product-card";

        card.innerHTML = `
            <img src="${product.image_path}" alt="${product.product_name}" />
            <h3 class="product-name">${product.product_name}</h3>
            <p class="product-price">Rs. ${product.price}</p>
           
            <button class="btn btn-sm btn-success add-btn" onclick="addToCart(${product.product_id}, '${product.product_name.replace(/'/g, "\\'")}', ${product.price})">
                <i class="bi bi-plus-circle"></i> Add
            </button>
        `;

        container.appendChild(card);
    });
}


function addToCart(product_id, name, price) {
    const existing = cart.find(item => item.product_id === product_id);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ product_id, name, price, quantity: 1 });
    }
    updateCartDisplay();
}

function removeFromCart(product_id) {
    cart = cart.filter(item => item.product_id !== product_id);
    updateCartDisplay();
}

function clearCart() {
    cart = [];
    updateCartDisplay();
    document.getElementById("paidAmount").value = '';
    document.getElementById("returnedAmount").value = '';
}

function updateCartDisplay() {
    const tbody = document.getElementById("cartTableBody");
    tbody.innerHTML = "";
    let total = 0;

    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.quantity}</td>
            <td>${item.name}</td>
            <td>${item.price.toFixed(2)}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="removeFromCart(${item.product_id})">
                    <i class="bi bi-x"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    document.getElementById("totalAmount").textContent = total.toFixed(2);
    document.getElementById("taxAmount").textContent = "0.00";
    document.getElementById("discountAmount").textContent = "0.00";

    updateBillingSummary();
}

function updateBillingSummary() {
    const paid = parseFloat(document.getElementById("paidAmount").value) || 0;
    const total = cart.reduce((acc, item) => acc + item.price * item.quantity, 0);
    const change = paid - total;

    document.getElementById("returnedAmount").value = change.toFixed(2);
}

async function saveOrder() {
    if (cart.length === 0) {
        alert("Cart is empty.");
        return;
    }

    const paidAmount = parseFloat(document.getElementById("paidAmount").value) || 0;
    const totalAmount = cart.reduce((acc, item) => acc + item.price * item.quantity, 0);
    const changeAmount = paidAmount - totalAmount;

    try {
        const response = await fetch('/api/save_order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cart: cart,
                paid_amount: paidAmount,
                change_amount: changeAmount
            })
        });

        const result = await response.json();

        if (result.success) {
            alert(`Order saved successfully! Order ID: ${result.order_id}`);
            window.open(result.pdf_url, '_blank'); // Open the PDF receipt
            clearCart();
            fetchProducts(); // Refresh stock
        }
         else {
            alert("Error saving order: " + result.error);
        }
    } catch (error) {
        console.error("Failed to save order:", error);
        alert("Something went wrong.");
    }
}

function newOrder() {
    clearCart();
}
