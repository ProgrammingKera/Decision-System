let cart = [];

// Fetch and display products
async function fetchProducts() {
    try {
        const res = await fetch("/api/products");
        const products = await res.json();
        displayProducts(products);
    } catch (err) {
        alert("Error fetching products: " + err.message);
    }
}

function displayProducts(products) {
    const productList = document.getElementById("product-list");
    productList.innerHTML = "";

    products.forEach(product => {
        const card = document.createElement("div");
        card.className = "product-card";
        card.innerHTML = `
            <img src="${product.image_path}" alt="${product.product_name}" class="product-image" />
            <div class="product-info">
                <h4>${product.product_name}</h4>
                <p>${product.category}</p>
                <p>${product.price} Pkr</p>
                <button onclick="addToCart('${product.product_name}', ${product.price})">Add</button>
            </div>
        `;
        productList.appendChild(card);
    });
}

// Add to cart
function addToCart(name, price) {
    const existing = cart.find(item => item.name === name);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ name, price, quantity: 1 });
    }
    updateCartDisplay();
}

// Update cart display
function updateCartDisplay() {
    const orderList = document.getElementById("order-list");
    const subtotalElem = document.getElementById("subtotal");
    const discountElem = document.getElementById("discount");
    const totalElem = document.getElementById("total");

    orderList.innerHTML = "";

    let subtotal = 0;

    cart.forEach(item => {
        subtotal += item.price * item.quantity;
        const row = document.createElement("div");
        row.innerHTML = `${item.name} - ${item.quantity} x ${item.price} = ${item.quantity * item.price} Pkr`;
        orderList.appendChild(row);
    });

    const discount = 0; 
    const total = subtotal - discount;

    subtotalElem.textContent = `${subtotal} Pkr`;
    discountElem.textContent = `${discount} Pkr`;
    totalElem.textContent = `${total} Pkr`;
}

// Clear cart
document.getElementById("clear-cart").addEventListener("click", () => {
    cart = [];
    updateCartDisplay();
});


document.getElementById("confirm-order").addEventListener("click", async () => {
    if (cart.length === 0) {
        alert("Cart is empty.");
        return;
    }

    
    const orderData = {
        supplier_name: "Default Supplier", 
        expected_delivery_date: new Date().toISOString().split('T')[0], // today's date
        items: cart
    };

    try {
        const res = await fetch('/save_pharmacy_order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });

        const data = await res.json();

        if (res.ok && data.pdf_url) {
            alert("Order placed successfully!");
            window.open(data.pdf_url, '_blank'); // open PDF
            cart = [];
            updateCartDisplay();
        } else {
            alert("Error: " + (data.error || "PDF not generated."));
        }

    } catch (error) {
        alert("Failed to confirm order: " + error.message);
    }
});


// Load products on page load
window.onload = fetchProducts;
