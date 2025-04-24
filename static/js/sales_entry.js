document.addEventListener('DOMContentLoaded', function() {
            // Initialize toast
            const downloadSuccessToast = new bootstrap.Toast(document.getElementById('downloadSuccessToast'), {autohide: true, delay: 3000});

            // Client search functionality
            const clientNameInput = document.getElementById('clientName');
            const searchClientBtn = document.getElementById('searchClientBtn');
            const clientSearchResults = document.getElementById('clientSearchResults');
            const clientSearchSection = document.getElementById('clientSearchSection');
            const transactionTypeSection = document.getElementById('transactionTypeSection');
            const salesFormSection = document.getElementById('salesFormSection');
            const customerNameDisplay = document.getElementById('customerNameDisplay');
            const invoiceNumber = document.getElementById('invoiceNumber');
            const invoiceDate = document.getElementById('invoiceDate');
            const invoiceItemsTable = document.getElementById('invoiceItems');
            const addAnotherSection = document.getElementById('addAnotherSection');
            const addAnotherYesBtn = document.getElementById('addAnotherYesBtn');
            const addAnotherNoBtn = document.getElementById('addAnotherNoBtn');
            const downloadInvoiceBtn = document.getElementById('downloadInvoiceBtn');
            const saveSaleBtn = document.getElementById('saveSaleBtn');
            const sellBtn = document.getElementById('sellBtn');
            const takeBackBtn = document.getElementById('takeBackBtn');
            const transactionTypeDisplay = document.getElementById('transactionTypeDisplay');
            const transactionTypeHeading = document.getElementById('transactionTypeHeading');
            const backToClientSearchBtn = document.getElementById('backToClientSearchBtn');
            const backToTransactionTypeBtn = document.getElementById('backToTransactionTypeBtn');

            let currentItems = [];
            let currentInvoiceUrl = '';
            let currentTransactionType = 'sell';

            // Search for client
            searchClientBtn.addEventListener('click', function() {
                const clientName = clientNameInput.value.trim();
                if (!clientName) return;

                fetch('/sales/entry', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `action=search_client&client_name=${encodeURIComponent(clientName)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'not_found') {
                        alert('Client not found. Please add the client first.');
                    } else if (data.status === 'single_result') {
                        selectClient(data.client_name);
                    } else if (data.status === 'multiple_results') {
                        showClientResults(data.clients);
                    }
                });
            });

            function showClientResults(clients) {
                clientSearchResults.innerHTML = '';
                clients.forEach(client => {
                    const item = document.createElement('div');
                    item.className = 'search-result-item';
                    item.textContent = client;
                    item.addEventListener('click', function() {
                        selectClient(client);
                    });
                    clientSearchResults.appendChild(item);
                });
                clientSearchResults.style.display = 'block';
            }

            function selectClient(clientName) {
                clientSearchResults.style.display = 'none';
                customerNameDisplay.value = clientName;

                // Get next invoice number and date
                fetch('/sales/entry', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `action=select_client&client_name=${encodeURIComponent(clientName)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        invoiceNumber.value = data.invoice_number;
                        invoiceDate.value = data.current_date;

                        // Switch to transaction type selection
                        clientSearchSection.classList.remove('active');
                        transactionTypeSection.classList.add('active');
                    }
                });
            }

            // Transaction type selection
            sellBtn.addEventListener('click', function() {
                currentTransactionType = 'sell';
                transactionTypeDisplay.value = 'Sell';
                transactionTypeHeading.textContent = 'Sale';
                proceedToSalesForm();
            });

            takeBackBtn.addEventListener('click', function() {
                currentTransactionType = 'take_back';
                transactionTypeDisplay.value = 'Take Back';
                transactionTypeHeading.textContent = 'Take Back';
                proceedToSalesForm();
            });

            function proceedToSalesForm() {
                transactionTypeSection.classList.remove('active');
                salesFormSection.classList.add('active');
            }

            // Navigation buttons
            backToClientSearchBtn.addEventListener('click', function() {
                transactionTypeSection.classList.remove('active');
                clientSearchSection.classList.add('active');
            });

            backToTransactionTypeBtn.addEventListener('click', function() {
                salesFormSection.classList.remove('active');
                transactionTypeSection.classList.add('active');
            });

            // Save sale
            saveSaleBtn.addEventListener('click', function() {
                const formData = {
                    invoice_date: invoiceDate.value,
                    invoice_number: invoiceNumber.value,
                    client_name: customerNameDisplay.value,
                    product: document.getElementById('product').value,
                    quantity: document.getElementById('quantity').value,
                    price: document.getElementById('price').value,
                    category: document.getElementById('category').value,
                    account: document.getElementById('account').value,
                    notes: document.getElementById('notes').value,
                    transaction_type: currentTransactionType,
                    add_another: 'no' // We'll handle this in the UI
                };

                // Basic validation
                if (!formData.product || !formData.price) {
                    alert('Please fill in all required fields');
                    return;
                }

                fetch('/sales/entry', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `action=save_sale&${new URLSearchParams(formData).toString()}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success' || data.status === 'add_another') {
                        // Add the new item to our current items array
                        const quantity = currentTransactionType === 'take_back' ?
                            -Math.abs(formData.quantity) : formData.quantity;

                        const newItem = {
                            description: formData.product,
                            quantity: quantity,
                            unitPrice: formData.price,
                            total: (quantity * formData.price).toFixed(2),
                            type: currentTransactionType
                        };
                        currentItems.push(newItem);
                        currentInvoiceUrl = data.invoice_url;

                        // Update invoice preview
                        updateInvoicePreview(
                            data.invoice_number,
                            formData.invoice_date,
                            formData.client_name,
                            currentTransactionType,
                            currentItems
                        );

                        // Show the "add another" section and hide the save button
                        saveSaleBtn.style.display = 'none';
                        addAnotherSection.style.display = 'block';
                        document.getElementById('invoicePreview').style.display = 'block';
                    } else {
                        alert(data.message);
                    }
                });
            });

            // Add another item
            addAnotherYesBtn.addEventListener('click', function() {
                // Reset product fields but keep invoice details
                document.getElementById('product').value = '';
                document.getElementById('quantity').value = '1';
                document.getElementById('price').value = '';
                document.getElementById('category').value = document.getElementById('category').options[0].value;
                document.getElementById('notes').value = '';

                // Hide add another section and show save button
                addAnotherSection.style.display = 'none';
                saveSaleBtn.style.display = 'block';

                // Focus on product field for next entry
                document.getElementById('product').focus();
            });

            // Don't add another item - download invoice
            addAnotherNoBtn.addEventListener('click', function() {
                if (currentInvoiceUrl) {
                    // Create a hidden iframe to trigger the download
                    const iframe = document.createElement('iframe');
                    iframe.style.display = 'none';
                    iframe.src = currentInvoiceUrl;
                    document.body.appendChild(iframe);

                    // Show success message
                    downloadSuccessToast.show();

                    // Redirect after download
                    setTimeout(function() {
                        window.location.href = '/sales';
                    }, 2000);
                }
            });

            // Download invoice button
            downloadInvoiceBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (currentInvoiceUrl) {
                    // Create a hidden iframe to trigger the download
                    const iframe = document.createElement('iframe');
                    iframe.style.display = 'none';
                    iframe.src = currentInvoiceUrl;
                    document.body.appendChild(iframe);

                    // Show success message
                    downloadSuccessToast.show();
                }
            });

            function updateInvoicePreview(invoiceNumber, invoiceDate, customerName, transactionType, items) {
                document.getElementById('previewInvoiceNumber').textContent = invoiceNumber;
                document.getElementById('previewDate').textContent = invoiceDate;
                document.getElementById('previewCustomer').textContent = customerName;
                document.getElementById('previewTransactionType').textContent =
                    transactionType === 'sell' ? 'Sale' : 'Take Back';

                // Clear existing items
                invoiceItemsTable.innerHTML = '';

                // Add all items
                let totalAmount = 0;
                items.forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${item.description}</td>
                        <td>${Math.abs(item.quantity)}</td>
                        <td>KSh ${parseFloat(item.unitPrice).toFixed(2)}</td>
                        <td>KSh ${parseFloat(item.total).toFixed(2)}</td>
                    `;
                    invoiceItemsTable.appendChild(row);
                    totalAmount += parseFloat(item.total);
                });

                // Update total
                document.getElementById('previewTotal').textContent = totalAmount.toFixed(2);
            }
        });

document.getElementById('addClientForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);

        fetch('/add_client_ajax', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Set the client name into the search field
                document.getElementById('clientName').value = data.customer_name;

                // Optionally hide the modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('addClientModal'));
                modal.hide();

                // Show success message
                alert('Client added successfully!');
            } else {
                alert('Error: ' + data.error);
            }
        });
    });