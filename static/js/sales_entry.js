document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements
    const downloadSuccessToast = new bootstrap.Toast(document.getElementById('downloadSuccessToast'), {autohide: true, delay: 3000});
    const clientNameInput = document.getElementById('clientName');
    const searchClientBtn = document.getElementById('searchClientBtn');
    const clientSearchResults = document.getElementById('clientSearchResults');
    const clientSuggestions = document.getElementById('clientSuggestions');
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
    const selectedClientDisplay = document.getElementById('selectedClientDisplay');
    const saveLoader = document.getElementById('saveLoader');

    // State variables
    let currentItems = [];
    let currentInvoiceUrl = '';
    let currentTransactionType = 'sell';
    const clientNames = window.clientNames || [];
    selectedClientDisplay.textContent = 'No client selected';

    // Required fields configuration
    const requiredFields = {
        'product': 'Product is required',
        'quantity': 'Quantity is required',
        'price': 'Price is required',
        'category': 'Category is required',
        'account': 'Account Owner is required',
        'bank_account': 'Bank Account is required'
    };

    // Field validation functions
    function validateField(fieldId, value) {
        const field = document.getElementById(fieldId);
        const fieldContainer = field.parentNode;
        let errorElement = fieldContainer.querySelector('.field-error-message');

        // Remove existing validation classes
        field.classList.remove('field-error', 'field-valid');

        if (requiredFields[fieldId]) {
            if (!value || value.trim() === '') {
                // Field is empty - show error
                field.classList.add('field-error');

                if (!errorElement) {
                    errorElement = document.createElement('div');
                    errorElement.className = 'field-error-message';
                    fieldContainer.appendChild(errorElement);
                }
                errorElement.textContent = requiredFields[fieldId];
                errorElement.classList.add('show');
                return false;
            } else {
                // Field has value - show valid
                field.classList.add('field-valid');
                if (errorElement) {
                    errorElement.classList.remove('show');
                }
                return true;
            }
        }
        return true;
    }

    function validateAllRequiredFields() {
        let allValid = true;
        const fieldValues = {};

        Object.keys(requiredFields).forEach(fieldId => {
            const field = document.getElementById(fieldId);
            const value = field.value;
            fieldValues[fieldId] = value;

            if (!validateField(fieldId, value)) {
                allValid = false;
            }
        });

        return { isValid: allValid, values: fieldValues };
    }

    // Add real-time validation listeners
    Object.keys(requiredFields).forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', function() {
                validateField(fieldId, this.value);
            });
            field.addEventListener('change', function() {
                validateField(fieldId, this.value);
            });
        }
    });

    // Helper function to stop loading
    function stopLoading() {
        saveSaleBtn.disabled = false;
        saveLoader.style.display = 'none';
    }

    // Helper function to start loading
    function startLoading() {
        saveSaleBtn.disabled = true;
        saveLoader.style.display = 'inline-block';
    }

    // Reset form for new item
    function resetFormForNewItem() {
        document.getElementById('product').value = '';
        document.getElementById('quantity').value = '1';
        document.getElementById('price').value = '';
        document.getElementById('category').value = '';
        document.getElementById('notes').value = '';

        // Clear validation styles
        Object.keys(requiredFields).forEach(fieldId => {
            const field = document.getElementById(fieldId);
            const fieldContainer = field.parentNode;
            const errorElement = fieldContainer.querySelector('.field-error-message');

            field.classList.remove('field-error', 'field-valid');
            if (errorElement) {
                errorElement.classList.remove('show');
            }
        });
    }

    // Reset entire form to start over
    function resetToClientSearch() {
        // Reset all sections
        salesFormSection.classList.remove('active');
        transactionTypeSection.classList.remove('active');
        clientSearchSection.classList.add('active');

        // Reset form
        resetFormForNewItem();
        document.getElementById('account').value = '';
        document.getElementById('bank_account').value = '';
        clientNameInput.value = '';
        selectedClientDisplay.textContent = 'No client selected';

        // Reset state
        currentItems = [];
        currentInvoiceUrl = '';

        // Hide sections
        addAnotherSection.style.display = 'none';
        document.getElementById('invoicePreview').style.display = 'none';
        document.getElementById('pdfLinksContainer').style.display = 'none';

        // Show save button
        saveSaleBtn.style.display = 'block';

        // Stop any loading
        stopLoading();
    }

    // Client search functionality
    clientNameInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        if (searchTerm.length < 1) {
            clientSuggestions.style.display = 'none';
            clientNameInput.classList.remove('suggesting');
            return;
        }

        const filteredClients = clientNames.filter(client =>
            client.toLowerCase().includes(searchTerm)).slice(0, 30);

        if (filteredClients.length > 0) {
            clientSuggestions.innerHTML = '';
            filteredClients.forEach(client => {
                const item = document.createElement('div');
                item.className = 'suggestion-item';
                item.textContent = client;
                item.addEventListener('click', function() {
                    clientNameInput.value = client;
                    clientSuggestions.style.display = 'none';
                    clientNameInput.classList.remove('suggesting');
                });
                clientSuggestions.appendChild(item);
            });
            clientSuggestions.style.display = 'block';
            clientNameInput.classList.add('suggesting');
        } else {
            clientSuggestions.style.display = 'none';
            clientNameInput.classList.remove('suggesting');
        }
    });

    document.addEventListener('click', function(e) {
        if (e.target !== clientNameInput && !clientSuggestions.contains(e.target)) {
            clientSuggestions.style.display = 'none';
            clientNameInput.classList.remove('suggesting');
        }
    });

    // Search button with empty input shows all clients in modal
    searchClientBtn.addEventListener('click', function() {
        const clientName = clientNameInput.value.trim();

        if (!clientName) {
            showAllClientsModal();
            return;
        }

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

    // Scrollable modal for all clients
    function showAllClientsModal() {
        const allClientsList = document.getElementById('allClientsList');
        allClientsList.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

        const modal = new bootstrap.Modal(document.getElementById('allClientsModal'));
        modal.show();

        if (clientNames && clientNames.length > 0) {
            populateClientList(clientNames);
        } else {
            fetch('/sales/entry', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'action=get_all_clients'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.clients.length > 0) {
                    populateClientList(data.clients);
                } else {
                    allClientsList.innerHTML = '<div class="list-group-item text-muted">No clients found</div>';
                }
            })
            .catch(error => {
                allClientsList.innerHTML = '<div class="list-group-item text-danger">Error loading clients</div>';
                console.error('Error fetching clients:', error);
            });
        }

        function populateClientList(clients) {
            allClientsList.innerHTML = '';
            clients.sort((a, b) => a.localeCompare(b));

            clients.forEach(client => {
                const clientItem = document.createElement('button');
                clientItem.type = 'button';
                clientItem.className = 'list-group-item list-group-item-action';
                clientItem.textContent = client;
                clientItem.addEventListener('click', function() {
                    selectClient(client);
                    modal.hide();
                });
                allClientsList.appendChild(clientItem);
            });
        }
    }

    function showClientResults(clients) {
        clientSearchResults.innerHTML = '';
        clientSuggestions.style.display = 'none';
        clientNameInput.classList.remove('suggesting');

        if (clients.length === 0) {
            clientSearchResults.style.display = 'none';
            return;
        }

        const chunkSize = 5;
        for (let i = 0; i < clients.length; i += chunkSize) {
            const chunk = clients.slice(i, i + chunkSize);
            const groupContainer = document.createElement('div');
            groupContainer.className = 'search-result-group';

            chunk.forEach(client => {
                const item = document.createElement('div');
                item.className = 'search-result-item';
                item.textContent = client;
                item.addEventListener('click', function() {
                    selectClient(client);
                });
                groupContainer.appendChild(item);
            });

            clientSearchResults.appendChild(groupContainer);
        }

        clientSearchResults.style.display = 'block';
    }

    function selectClient(clientName) {
        clientSearchResults.style.display = 'none';
        clientSuggestions.style.display = 'none';
        clientNameInput.classList.remove('suggesting');
        customerNameDisplay.value = clientName;
        selectedClientDisplay.textContent = clientName;

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
        selectedClientDisplay.textContent = customerNameDisplay.value || 'No client selected';
        salesFormSection.classList.remove('active');
        transactionTypeSection.classList.add('active');
    });

    // Save sale functionality
    saveSaleBtn.addEventListener('click', function() {
        // Validate all required fields
        const validation = validateAllRequiredFields();

        if (!validation.isValid) {
            alert('Please fill in all required fields');
            return;
        }

        startLoading();

        const formData = {
            invoice_date: invoiceDate.value,
            invoice_number: invoiceNumber.value,
            client_name: customerNameDisplay.value,
            product: document.getElementById('product').value,
            quantity: document.getElementById('quantity').value,
            price: document.getElementById('price').value,
            category: document.getElementById('category').value,
            account: document.getElementById('account').value,
            bank_account: document.getElementById('bank_account').value,
            notes: document.getElementById('notes').value,
            transaction_type: currentTransactionType,
            add_another: 'no'
        };

        fetch('/sales/entry', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `action=save_sale&${new URLSearchParams(formData).toString()}`
        })
        .then(response => response.json())
        .then(data => {
            stopLoading();

            if (data.status === 'success' || data.status === 'add_another') {
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

                if (data.pdf_urls){
                    showMultiplePdfLinks(data.pdf_urls);
                    currentInvoiceUrl = data.pdf_urls[0].url;
                } else{
                    currentInvoiceUrl = data.invoice_url;
                }

                // Hide save button and show add another section
                saveSaleBtn.style.display = 'none';
                addAnotherSection.style.display = 'block';

                // Don't show preview yet - wait for user decision
            } else {
                alert(data.message || 'An error occurred while saving the sale');
            }
        })
        .catch(error => {
            stopLoading();
            console.error('Error saving sale:', error);
            alert('An error occurred while saving the sale');
        });
    });

    // Function to show multiple PDF links
    function showMultiplePdfLinks(pdfUrls){
        const pdfLinksContainer = document.getElementById('pdfLinksContainer');
        pdfLinksContainer.innerHTML = '<h6>Generated Invoices:</h6>';

        pdfUrls.forEach(pdf => {
            const link = document.createElement('a');
            link.href = pdf.url;
            link.className = 'd-block mb-2';
            link.textContent = `Download ${pdf.date} Invoice`;
            link.target = '_blank';
            pdfLinksContainer.appendChild(link);
        });

        pdfLinksContainer.style.display = 'block';
    }

    // Add another item
    addAnotherYesBtn.addEventListener('click', function() {
        resetFormForNewItem();
        addAnotherSection.style.display = 'none';
        saveSaleBtn.style.display = 'block';
        document.getElementById('product').focus();
    });

    // Finish and show preview
    addAnotherNoBtn.addEventListener('click', function() {
        addAnotherSection.style.display = 'none';

        // Now show the invoice preview
        updateInvoicePreview(
            invoiceNumber.value,
            invoiceDate.value,
            customerNameDisplay.value,
            currentTransactionType,
            currentItems
        );

        document.getElementById('invoicePreview').style.display = 'block';
    });

    // Download invoice
    downloadInvoiceBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (currentInvoiceUrl) {
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = currentInvoiceUrl;
            document.body.appendChild(iframe);
            downloadSuccessToast.show();

            // Return to client search instead of exiting
            setTimeout(function() {
                resetToClientSearch();
            }, 2000);
        }
    });

    function updateInvoicePreview(invoiceNumber, invoiceDate, customerName, transactionType, items) {
        document.getElementById('previewInvoiceNumber').textContent = invoiceNumber;
        document.getElementById('previewDate').textContent = invoiceDate;
        document.getElementById('previewCustomer').textContent = customerName;
        document.getElementById('previewTransactionType').textContent =
            transactionType === 'sell' ? 'Sale' : 'Take Back';

        invoiceItemsTable.innerHTML = '';
        let totalAmount = 0;

        items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.description}</td>
                <td>${Math.abs(item.quantity)}</td>
                <td>Ksh ${parseFloat(item.unitPrice).toFixed(2)}</td>
                <td>Ksh ${parseFloat(item.total).toFixed(2)}</td>
            `;
            invoiceItemsTable.appendChild(row);
            totalAmount += parseFloat(item.total);
        });

        document.getElementById('previewTotal').textContent = totalAmount.toFixed(2);
    }
});

// Add client form submission
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
            document.getElementById('clientName').value = data.customer_name;
            const modal = bootstrap.Modal.getInstance(document.getElementById('addClientModal'));
            modal.hide();
            alert('Client added successfully!');
            if (typeof clientNames !== 'undefined') {
                clientNames.push(data.customer_name);
            }
        } else {
            alert('Error: ' + data.error);
        }
    });
});