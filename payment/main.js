import './style.css';

// Initialize Stripe (you'll need to replace with your actual publishable key)
const stripe = Stripe('pk_test_51234567890abcdef'); // Replace with your Stripe publishable key

let orderData = null;

// Load order data from sessionStorage
document.addEventListener('DOMContentLoaded', () => {
    loadOrderData();
    initializePaymentForm();
});

function loadOrderData() {
    const storedOrder = sessionStorage.getItem('pendingOrder');
    if (storedOrder) {
        orderData = JSON.parse(storedOrder);
        populateOrderSummary();
    } else {
        // Redirect back to customer page if no order data
        window.location.href = '/customer';
    }
}

function populateOrderSummary() {
    const orderItemsContainer = document.getElementById('orderItems');
    const subtotalElement = document.getElementById('subtotalAmount');
    const grandTotalElement = document.getElementById('grandTotal');

    if (!orderData || !orderData.cart) return;

    // Clear existing items
    orderItemsContainer.innerHTML = '';

    // Populate order items
    orderData.cart.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'order-item';
        itemElement.innerHTML = `
            <div class="item-details">
                <h3>${item.name}</h3>
                <p>Quantity: ${item.quantity} × Rs. ${item.price.toFixed(2)}</p>
            </div>
            <span class="item-price">Rs. ${(item.price * item.quantity).toFixed(2)}</span>
        `;
        orderItemsContainer.appendChild(itemElement);
    });

    // Update totals
    const total = orderData.total || 0;
    subtotalElement.textContent = `Rs. ${total.toFixed(2)}`;
    grandTotalElement.textContent = `Rs. ${total.toFixed(2)}`;
}

function initializePaymentForm() {
    // Card formatting and display functions
    function formatCardNumber(value) {
        const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
        const matches = v.match(/\d{4,16}/g);
        const match = matches && matches[0] || '';
        const parts = [];
        
        for (let i = 0, len = match.length; i < len; i += 4) {
            parts.push(match.substring(i, i + 4));
        }
        
        if (parts.length) {
            return parts.join(' ');
        } else {
            return value;
        }
    }

    function formatExpiryDate(value) {
        const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
        
        if (v.length >= 3) {
            return `${v.substring(0, 2)}/${v.substring(2, 4)}`;
        }
        
        return value;
    }

    // DOM elements
    const cardElement = document.getElementById('creditCard');
    const cardNumberInput = document.getElementById('cardNumber');
    const cardHolderInput = document.getElementById('cardHolder');
    const expiryDateInput = document.getElementById('expiryDate');
    const cvvInput = document.getElementById('cvv');
    const paymentForm = document.getElementById('paymentForm');
    const successModal = document.getElementById('successModal');
    const downloadReceiptBtn = document.getElementById('downloadReceipt');
    const continueShoppingBtn = document.getElementById('continueShopping');
    const paymentOptions = document.querySelectorAll('.payment-option');

    // Display elements
    const cardNumberDisplay = document.getElementById('cardNumberDisplay');
    const cardHolderDisplay = document.getElementById('cardHolderDisplay');
    const expiryDisplay = document.getElementById('expiryDisplay');
    const cvvDisplay = document.getElementById('cvvDisplay');

    // Error message elements
    const cardNumberError = document.getElementById('cardNumberError');
    const cardHolderError = document.getElementById('cardHolderError');
    const expiryDateError = document.getElementById('expiryDateError');
    const cvvError = document.getElementById('cvvError');

    // Event listeners for input fields
    cardNumberInput.addEventListener('input', (e) => {
        let value = e.target.value;
        e.target.value = formatCardNumber(value);
        
        // Update card display with animation
        cardNumberDisplay.classList.add('animate');
        setTimeout(() => {
            cardNumberDisplay.textContent = e.target.value || '•••• •••• •••• ••••';
            cardNumberDisplay.classList.remove('animate');
        }, 300);
    });

    cardHolderInput.addEventListener('input', (e) => {
        // Update card display with animation
        cardHolderDisplay.classList.add('animate');
        setTimeout(() => {
            cardHolderDisplay.textContent = e.target.value.toUpperCase() || 'YOUR NAME';
            cardHolderDisplay.classList.remove('animate');
        }, 150);
    });

    expiryDateInput.addEventListener('input', (e) => {
        let value = e.target.value;
        e.target.value = formatExpiryDate(value);
        expiryDisplay.textContent = e.target.value || 'MM/YY';
    });

    cvvInput.addEventListener('focus', () => {
        cardElement.classList.add('flipped');
    });

    cvvInput.addEventListener('blur', () => {
        cardElement.classList.remove('flipped');
    });

    cvvInput.addEventListener('input', (e) => {
        cvvDisplay.textContent = e.target.value || '•••';
    });

    // Payment method selection
    paymentOptions.forEach(option => {
        option.addEventListener('click', () => {
            // Remove active class from all options
            paymentOptions.forEach(opt => opt.classList.remove('active'));
            // Add active class to clicked option
            option.classList.add('active');
            // Check the radio button
            const radio = option.querySelector('input[type="radio"]');
            radio.checked = true;
        });
    });

    // Form validation functions
    function validateCardNumber(number) {
        const cardNumber = number.replace(/\s/g, '');
        if (cardNumber.length < 16) {
            return { valid: false, message: 'Please enter a valid 16-digit card number' };
        }
        return { valid: true, message: '' };
    }

    function validateCardHolder(name) {
        if (!name || name.trim().length < 3) {
            return { valid: false, message: 'Please enter the cardholder name' };
        }
        return { valid: true, message: '' };
    }

    function validateExpiryDate(expiry) {
        if (!expiry || expiry.length < 5) {
            return { valid: false, message: 'Enter a valid date (MM/YY)' };
        }
        
        const [month, year] = expiry.split('/');
        const currentYear = new Date().getFullYear() % 100;
        const currentMonth = new Date().getMonth() + 1;
        
        if (parseInt(month) < 1 || parseInt(month) > 12) {
            return { valid: false, message: 'Invalid month (1-12)' };
        }
        
        if (parseInt(year) < currentYear || 
            (parseInt(year) === currentYear && parseInt(month) < currentMonth)) {
            return { valid: false, message: 'Card has expired' };
        }
        
        return { valid: true, message: '' };
    }

    function validateCVV(cvv) {
        if (!cvv || cvv.length < 3) {
            return { valid: false, message: 'Enter a valid 3-digit CVV' };
        }
        return { valid: true, message: '' };
    }

    // Form submission
    paymentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validate all fields
        let valid = true;
        
        const cardNumberValidation = validateCardNumber(cardNumberInput.value);
        if (!cardNumberValidation.valid) {
            cardNumberError.textContent = cardNumberValidation.message;
            cardNumberInput.classList.add('error');
            valid = false;
        } else {
            cardNumberError.textContent = '';
            cardNumberInput.classList.remove('error');
        }
        
        const cardHolderValidation = validateCardHolder(cardHolderInput.value);
        if (!cardHolderValidation.valid) {
            cardHolderError.textContent = cardHolderValidation.message;
            cardHolderInput.classList.add('error');
            valid = false;
        } else {
            cardHolderError.textContent = '';
            cardHolderInput.classList.remove('error');
        }
        
        const expiryValidation = validateExpiryDate(expiryDateInput.value);
        if (!expiryValidation.valid) {
            expiryDateError.textContent = expiryValidation.message;
            expiryDateInput.classList.add('error');
            valid = false;
        } else {
            expiryDateError.textContent = '';
            expiryDateInput.classList.remove('error');
        }
        
        const cvvValidation = validateCVV(cvvInput.value);
        if (!cvvValidation.valid) {
            cvvError.textContent = cvvValidation.message;
            cvvInput.classList.add('error');
            valid = false;
        } else {
            cvvError.textContent = '';
            cvvInput.classList.remove('error');
        }
        
        if (valid) {
            await processPayment();
        }
    });

    async function processPayment() {
        const payButton = paymentForm.querySelector('.pay-button');
        payButton.classList.add('loading');
        payButton.innerHTML = '<span>Processing...</span>';
        
        try {
            // Simulate payment processing with Stripe
            // In a real implementation, you would create a payment intent on your backend
            // and use Stripe's confirmCardPayment method
            
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Save order to backend
            const response = await fetch('/api/save_order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cart: orderData.cart,
                    paid_amount: orderData.total,
                    change_amount: 0,
                    payment_method: 'stripe',
                    card_holder: cardHolderInput.value,
                    card_last_four: cardNumberInput.value.slice(-4)
                })
            });

            const result = await response.json();

            if (result.success) {
                // Store receipt URL for download
                sessionStorage.setItem('receiptUrl', result.pdf_url);
                sessionStorage.setItem('orderId', result.order_id);
                
                // Clear pending order
                sessionStorage.removeItem('pendingOrder');
                
                // Show success modal
                successModal.classList.add('show');
            } else {
                throw new Error(result.error || 'Payment failed');
            }
        } catch (error) {
            console.error('Payment error:', error);
            alert('Payment failed: ' + error.message);
        } finally {
            payButton.classList.remove('loading');
            payButton.innerHTML = '<span>Pay Now</span><span class="button-icon">→</span>';
        }
    }

    // Modal event handlers
    downloadReceiptBtn.addEventListener('click', () => {
        const receiptUrl = sessionStorage.getItem('receiptUrl');
        if (receiptUrl) {
            window.open(receiptUrl, '_blank');
        }
    });

    continueShoppingBtn.addEventListener('click', () => {
        window.location.href = '/customer';
    });
}