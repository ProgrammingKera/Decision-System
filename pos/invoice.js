document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('invoiceDisplay').style.display = 'none';
});

function searchInvoice() {
    const invoiceNumber = document.getElementById('invoiceNumber').value.trim();
    const invoiceDisplay = document.getElementById('invoiceDisplay');

    if (invoiceNumber === '') {
        alert('Please enter an invoice number');
        return;
    }

    fetch(`/api/invoice/${invoiceNumber}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Invoice not found');
            }
            return response.json();
        })
        .then(data => {
            if (!data || !data.order || data.items.length === 0) {
                invoiceDisplay.innerHTML = `<p>No invoice found for ID ${invoiceNumber}</p>`;
                invoiceDisplay.style.display = 'block';
                return;
            }

            const { order, items } = data;
            const date = new Date(order.order_date).toLocaleDateString();

            let invoiceHTML = `
                <div class="invoice-header">
                    <h3>Invoice #${invoiceNumber}</h3>
                    <span class="date"><i class="far fa-calendar-alt"></i> ${date}</span>
                </div>
                <div class="customer-info">
                    <p><i class="far fa-user"></i> <strong>Customer:</strong> ID ${order.customer_id}</p>
                </div>
                <table class="invoice-items">
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Quantity</th>
                            <th>Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>`;

            let total = 0;
            items.forEach(item => {
                const itemTotal = parseFloat(item.total_price) || 0;
                total += itemTotal;

                invoiceHTML += `
                    <tr>
                        <td>${item.product_name}</td>
                        <td>${item.quantity}</td>
                        <td>Rs. ${parseFloat(item.unit_price).toFixed(2)}</td>
                        <td>Rs. ${itemTotal.toFixed(2)}</td>
                    </tr>`;
            });

            invoiceHTML += `</tbody>
                <tfoot>
                    <tr>
                        <td colspan="3"><strong>Total Amount</strong></td>
                        <td><strong>Rs. ${total.toFixed(2)}</strong></td>
                    </tr>
                    <tr>
                        <td colspan="3"><strong>Paid</strong></td>
                        <td><strong>Rs. ${(parseFloat(order.paid_amount) || 0).toFixed(2)}</strong></td>
                    </tr>
                    <tr>
                        <td colspan="3"><strong>Change Returned</strong></td>
                        <td><strong>Rs. ${(parseFloat(order.change_amount) || 0).toFixed(2)}</strong></td>
                    </tr>
                </tfoot>
                </table>
            `;

            invoiceDisplay.innerHTML = invoiceHTML;
            invoiceDisplay.style.display = 'block';
        })
        .catch(err => {
            invoiceDisplay.innerHTML = `<p style="color:red;">${err.message}</p>`;
            invoiceDisplay.style.display = 'block';
        });
}
