document.addEventListener("DOMContentLoaded", () => {
    console.log(" DOM Loaded, Fetching Products...");
    fetchProducts();
});

// backend se data fetch
function fetchProducts() {
    fetch("http://127.0.0.1:5000/api/products")  
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(" Fetched Products:", data); 
            renderProducts(data);
        })
        .catch(error => {
            console.error(" Error fetching products:", error);
        });
}

function renderProducts(products) {
    const tableBody = document.getElementById("productTableBody");

    if (!tableBody) {
        console.error(" Table body not found!");
        return;
    }

    tableBody.innerHTML = ''; 

    products.forEach(product => {
        const row = document.createElement("tr");

        // default image fallback
        const imagePath = product.image_path ? product.image_path : '/pictures/default.jpg';

        row.innerHTML = `
            <td><img src="${imagePath}" alt="${product.product_name}" class="product-image"></td>
            <td>${product.product_name}</td>
            <td>${product.product_id}</td>
            <td>${product.stock_quantity}</td>
            <td>${product.expiry_date ? formatDate(product.expiry_date) : 'N/A'}</td>
            <td>${product.price} PKR</td>
            <td>${calculateSellingPrice(product.price)} PKR</td>
            <td><button class="actions-btn">⋮</button></td>
        `;
        tableBody.appendChild(row);
    });

    console.log("✅ Products Rendered!");
}

function formatDate(dateString) {
    const date = new Date(dateString);
    if (isNaN(date)) return "Invalid Date";
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${date.getDate()} ${months[date.getMonth()]}, ${date.getFullYear()}`;
}

function calculateSellingPrice(costPrice) {
    return (parseFloat(costPrice) * 1.2).toFixed(2); 
}
