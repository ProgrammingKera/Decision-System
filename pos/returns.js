document.getElementById('invoice-form').addEventListener('submit', function(event) {
    event.preventDefault();
    document.getElementById('claim-invoice').classList.add('hidden');
    document.getElementById('process-return').classList.remove('hidden');
});

function updateTotal() {
    const quantity = document.getElementById('quantity').value;
    const price = document.getElementById('price').value;
    const total = (quantity * price).toFixed(2);
    document.getElementById('total').value = total;
}

document.getElementById('quantity').addEventListener('input', updateTotal);
document.getElementById('price').addEventListener('input', updateTotal);

function increaseQuantity() {
    let quantityInput = document.getElementById('number-of-products');
    let currentQuantity = parseInt(quantityInput.value, 10);
    quantityInput.value = currentQuantity + 1;
    updateTotal();
}

function decreaseQuantity() {
    let quantityInput = document.getElementById('number-of-products');
    let currentQuantity = parseInt(quantityInput.value, 10);
    if (currentQuantity > 1) {
        quantityInput.value = currentQuantity - 1;
        updateTotal();
    }
}