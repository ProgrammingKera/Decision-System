import './style.css';

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

function maskCardDisplay(cardNumber) {
  if (!cardNumber) return '•••• •••• •••• ••••';
  
  const parts = cardNumber.split(' ');
  if (parts.length === 4) {
    return `•••• •••• •••• ${parts[3]}`;
  }
  
  return cardNumber;
}

// DOM elements
const cardElement = document.getElementById('creditCard');
const cardNumberInput = document.getElementById('cardNumber');
const cardHolderInput = document.getElementById('cardHolder');
const expiryDateInput = document.getElementById('expiryDate');
const cvvInput = document.getElementById('cvv');
const paymentForm = document.getElementById('paymentForm');
const successModal = document.getElementById('successModal');
const closeModalBtn = document.getElementById('closeModal');
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
    cardHolderDisplay.textContent = e.target.value || 'YOUR NAME';
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

// Form validation
function validateCardNumber(number) {
  // Basic validation - check if card number is complete
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

// Form submission
paymentForm.addEventListener('submit', (e) => {
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
    const payButton = paymentForm.querySelector('.pay-button');
    payButton.classList.add('loading');
    payButton.innerHTML = '<span>Processing...</span>';
    
    // Simulate payment processing
    setTimeout(() => {
      // Show success modal
      successModal.classList.add('show');
      payButton.classList.remove('loading');
      payButton.innerHTML = '<span>Pay Now</span><span class="button-icon">→</span>';
    }, 2000);
  }
});

// Close modal event
closeModalBtn.addEventListener('click', () => {
  successModal.classList.remove('show');
});

// Initialize animations for card number on page load
setTimeout(() => {
  cardNumberDisplay.classList.add('animate');
  setTimeout(() => {
    cardNumberDisplay.classList.remove('animate');
  }, 300);
}, 500);