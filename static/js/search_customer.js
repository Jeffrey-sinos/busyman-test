$(document).ready(function() {
    const recordPaymentUrlBase = "/record_payment";
    let searchTimeout;

    // Debounced autocomplete search - now triggers after 1 character
    $('#customerSearch').on('input', function() {
        const searchTerm = $(this).val().trim();

        // Show suggestions immediately for any input
        if (searchTerm.length > 0) {
            fetchCustomers(searchTerm);
        } else {
            $('#searchSuggestions').hide();
        }
    });

    // Search button click
    $('#searchBtn').click(function() {
        const searchTerm = $('#customerSearch').val().trim();
        if (searchTerm.length > 0) {
            fetchCustomers(searchTerm, true);
        } else {
            // Show modal with all customers when search term is empty
            showAllCustomersModal();
        }
    });

    // Function to show all customers modal
    function showAllCustomersModal() {
        const modal = new bootstrap.Modal(document.getElementById('allCustomersModal'));
        modal.show();

        // Load all customers with unpaid invoices
        loadAllCustomers();
    }

    // Function to load all customers with unpaid invoices
    // Function to load all customers with unpaid invoices
function loadAllCustomers() {
    const tbody = $('#allCustomersTable tbody');
    tbody.html(`
        <tr>
            <td colspan="2" class="text-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                Loading all customers with unpaid invoices...
            </td>
        </tr>
    `);

    $.get('/search_customers', {term: ''})
        .done(function(data) {
            tbody.empty();

            if (Array.isArray(data) && data.length > 0) {
                // Update customer count badge
                $('#customerCount').text(`${data.length} customers`);

                data.forEach(function(customer) {
                    const row = `
                        <tr class="customer-list-item">
                            <td>${escapeHtml(customer)}</td>
                            <td>
                                <button class="btn btn-sm btn-primary select-customer-btn"
                                        data-customer="${escapeHtml(customer)}">
                                    <i class="bi bi-eye me-1"></i> View Invoices
                                </button>
                            </td>
                        </tr>
                    `;
                    tbody.append(row);
                });

                // Show message if many customers are loaded
//                if (data.length > 50) {
//                    tbody.prepend(`
//                        <tr class="table-info">
//                            <td colspan="2" class="text-center fw-bold">
//                                <i class="bi bi-info-circle me-2"></i>
//                                Showing all ${data.length} customers with unpaid invoices
//                            </td>
//                        </tr>
//                    `);
//                }
            } else {
                tbody.append(`
                    <tr>
                        <td colspan="2" class="text-center text-muted">
                            <i class="bi bi-check-circle me-2"></i>
                            No customers with unpaid invoices found
                        </td>
                    </tr>
                `);
                $('#customerCount').text('0 customers');
            }
        })
        .fail(function() {
            tbody.html(`
                <tr>
                    <td colspan="2" class="text-center text-danger">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        Error loading customers. Please try again.
                    </td>
                </tr>
            `);
            $('#customerCount').text('Error');
        });
}

    // Handle customer selection from all customers modal
    $(document).on('click', '.select-customer-btn', function() {
        const customerName = $(this).data('customer');
        $('#customerSearch').val(customerName);
        $('#allCustomersModal').modal('hide');
        loadUnpaidInvoices(customerName);
    });

    // Function to fetch customers for autocomplete
    function fetchCustomers(searchTerm) {
        $.get('/search_customers', {term: searchTerm})
            .done(function (data) {
                const suggestions = $('#searchSuggestions');
                suggestions.empty();

                if (Array.isArray(data) && data.length > 0) {
                    data.slice(0, 5).forEach(function (customer) {
                        suggestions.append(`
                        <div class="list-group-item list-group-item-action suggestion-item"
                             data-customer="${escapeHtml(customer)}">
                            <i class="bi bi-person me-2"></i>${escapeHtml(customer)}
                        </div>
                    `);
                    });
                    suggestions.show();
                } else {
                    suggestions.hide();
                }
            })
            .fail(function () {
                $('#searchSuggestions').hide();
            });
    }

    // Handle customer selection from suggestions
    $(document).on('click', '.suggestion-item', function() {
        const customerName = $(this).data('customer');
        $('#customerSearch').val(customerName);
        $('#searchSuggestions').hide();
        loadUnpaidInvoices(customerName);
    });

    // Function to load unpaid invoices
    function loadUnpaidInvoices(customerName) {
        $('#selectedCustomer').text(customerName);
        $('#unpaidInvoices').show();
        $('#invoicesTable tbody').html(`
            <tr>
                <td colspan="6" class="text-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    Loading invoices...
                </td>
            </tr>
        `);

        $.get(`/get_unpaid_invoices/${encodeURIComponent(customerName)}`)
            .done(function(data) {
                const tbody = $('#invoicesTable tbody');
                tbody.empty();

                if (data.status === "success" && data.invoices && data.invoices.length > 0) {
                    let totalBalance = 0;

                    data.invoices.forEach(function(invoice) {
                        totalBalance += parseFloat(invoice.balance || 0);

                        // Format invoice date properly
                        const invoiceDate = new Date(invoice.invoice_date);
                        const formattedInvoiceDate = isNaN(invoiceDate.getTime()) ?
                            invoice.invoice_date :
                            invoiceDate.toISOString().split('T')[0];

                        const row = `
                            <tr>
                                <td><strong>${escapeHtml(invoice.invoice_no)}</strong></td>
                                <td>${formatDate(invoice.invoice_date)}</td>
                                <td>Ksh ${parseFloat(invoice.invoice_amount).toFixed(2)}</td>
                                <td class="paid-amount">Ksh ${parseFloat(invoice.paid_amount).toFixed(2)}</td>
                                <td class="balance-amount">Ksh ${parseFloat(invoice.balance).toFixed(2)}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary payment-btn handle-payment-btn"
                                            data-sales-list-id="${invoice.id}"
                                            data-invoice-no="${escapeHtml(invoice.invoice_no)}"
                                            data-customer-name="${escapeHtml(customerName)}"
                                            data-invoice-date="${formattedInvoiceDate}"
                                            data-category="${invoice.category}"
                                            data-invoice-amount="${invoice.invoice_amount}"
                                            data-account-owner="${invoice.account_owner}"
                                            data-balance="${invoice.balance}"
                                            data-paid-amount="${invoice.paid_amount}"
                                            data-payment-status="${invoice.payment_status}">
                                         Receive
                                    </button>
                                </td>
                            </tr>
                        `;
                        tbody.append(row);
                    });

                    $('#totalBalance').text(`Ksh ${totalBalance.toFixed(2)}`);
                } else {
                    tbody.append(`
                        <tr>
                            <td colspan="6" class="text-center text-muted">
                                <i class="bi bi-check-circle me-2"></i>
                                No unpaid invoices found for this customer
                            </td>
                        </tr>
                    `);
                    $('#totalBalance').text('Ksh 0.00');
                }
            })
            .fail(function() {
                showAlert('Error loading invoices. Please try again.', 'danger');
                $('#invoicesTable tbody').html(`
                    <tr>
                        <td colspan="6" class="text-center text-danger">
                            <i class="bi bi-exclamation-triangle me-2"></i>
                            Error loading invoices
                        </td>
                    </tr>
                `);
            });
    }

    // Handle payment button click
    $(document).on('click', '.handle-payment-btn', function(e) {
        e.preventDefault();
        const salesListId = $(this).data('sales-list-id');
        const invoiceNo = $(this).data('invoice-no');
        const invoiceDate = $(this).data('invoice-date');
        const customerName = $(this).data('customer-name');
        const invoiceAmount = $(this).data('invoice-amount');
        const paidAmount = $(this).data('paid-amount');
        const balance = $(this).data('balance');
        const category = $(this).data('category');
        const accountOwner = $(this).data('account-owner');
        const paymentStatus = $(this).data('payment-status');

        showPaymentModal(salesListId, invoiceNo, invoiceDate, customerName,invoiceAmount, paidAmount, balance, category, accountOwner, paymentStatus);
    });

    // Show payment modal
    function showPaymentModal(salesListId, invoiceNo, invoiceDate, customerName, invoiceAmount, paidAmount, balance, category, accountOwner, paymentStatus) {
        const modalHtml = `
            <div class="modal fade" id="paymentModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Record Payment</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <form id="paymentForm">
                                <input type="hidden" name="sales_list_id" value="${salesListId}">
                                <input type="hidden" name="invoice_no" value="${invoiceNo}">
                                <input type="hidden" name="customer_name" value="${escapeHtml(customerName)}">
                                <input type="hidden" name="category" value="${category}">
                                <input type="hidden" name="account_owner" value="${accountOwner}">

                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <label class="form-label">Invoice Date</label>
                                        <input type="date" class="form-control" name="invoice_date"
                                               value="${invoiceDate}" readonly>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Invoice Number</label>
                                        <input type="text" class="form-control" name="invoice_no"
                                               value="${invoiceNo}" readonly>
                                    </div>

                                    <div class="col-md-6">
                                        <label class="form-label">Invoice Amount</label>
                                        <input type="number" class="form-control" name="invoice_amount"
                                               value="${invoiceAmount}" readonly>
                                    </div>

                                    <div class="col-md-6">
                                        <label class="form-label">Amount Paid</label>
                                        <input type="number" class="form-control editable-field paid-amount-input" name="paid_amount"
                                             value="${paidAmount}"  max="${invoiceAmount}" min="0" step="0.01" required>
                                        <small class="text-danger amount-warning" style="display: none;">
                                            <i class="bi bi-exclamation-circle"></i> Cannot exceed invoice amount
                                        </small>
                                    </div>

                                    <div class="col-md-6">
                                        <label class="form-label">Balance</label>
                                        <input type="number" class="form-control balance-amount"
                                               value="${balance}" readonly>
                                    </div>

                                    <div class="col-md-6">
                                        <label class="form-label">Status</label>
                                        <input type="text" class="form-control payment-status"
                                               value="${paymentStatus}" readonly>
                                    </div>

                                    <div class="col-md-6">
                                        <label class="form-label">Category</label>
                                        <input type="text" class="form-control" name="category"
                                               value="${category}" readonly>
                                    </div>

                                    <div class="col-md-6">
                                        <label class="form-label">Account Owner</label>
                                        <input type="text" class="form-control" name="account_owner"
                                               value="${accountOwner}" readonly>
                                    </div>
                                </div>

                                <div class="modal-footer mt-3">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                    <button type="submit" class="btn btn-primary">
                                        <i class="bi bi-save me-1"></i> Save Payment
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;

        $('body').append(modalHtml);
        const paymentModal = new bootstrap.Modal(document.getElementById('paymentModal'));
        paymentModal.show();

        // Live balance calculation
        $('.paid-amount-input').on('input', function() {
            const paidAmount = parseFloat($(this).val()) || 0;
            const invoiceAmount = parseFloat($('input[name="invoice_amount"]').val());
            const balance = invoiceAmount - paidAmount;

            // Update balance field
            $('.balance-amount').val(balance.toFixed(2));

            // Update status
            if (balance <= 0) {
                $('.payment-status').val('Paid');
            } else {
                $('.payment-status').val('Not Paid');
            }

            // Show warning if paid amount exceeds invoice amount
            if (paidAmount > invoiceAmount) {
                $('.amount-warning').show();
                $('.paid-amount-input').addClass('is-invalid');
            } else {
                $('.amount-warning').hide();
                $('.paid-amount-input').removeClass('is-invalid');
            }
        });

        // Handle form submission
        $('#paymentForm').on('submit', function(e) {
            e.preventDefault();

            const $submitBtn = $(this).find('button[type="submit"]');
            $submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1" role="status"></span> Processing...');

            // Validate payment amount
            const paidAmount = parseFloat($('.paid-amount-input').val());
            const invoiceAmount = parseFloat($('input[name="invoice_amount"]').val());

            if (paidAmount > invoiceAmount) {
                showAlert('Payment amount cannot exceed invoice amount', 'danger');
                $submitBtn.prop('disabled', false).html('<i class="bi bi-save me-1"></i> Save Payment');
                return;
            }

            const balance = parseFloat($('.balance-amount').val());
            const paymentStatus = balance <= 0 ? 'Paid' : 'Not Paid';

            const formData = {
                sales_list_id: salesListId,
                invoice_no: invoiceNo,
                invoice_date: invoiceDate,
                customer_name: $('input[name="customer_name"]').val(),
                category: category,
                account_owner: accountOwner,
                invoice_amount: invoiceAmount,
                paid_amount: paidAmount,
                payment_status: paymentStatus,
            };

            $.ajax({
                url: `${recordPaymentUrlBase}/${salesListId}`,
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(formData),
                success: function(response) {
                    if (response.success) {
                        showAlert(response.message, 'success');
                        paymentModal.hide();
                        loadUnpaidInvoices(customerName);
                    } else {
                        showAlert('Error: ' + response.message, 'danger');
                        $submitBtn.prop('disabled', false).html('<i class="bi bi-save me-1"></i> Save Payment');
                    }
                },
                error: function(xhr) {
                    const errorMsg = xhr.responseJSON?.message || 'Server error';
                    showAlert('Error: ' + errorMsg, 'danger');
                    $submitBtn.prop('disabled', false).html('<i class="bi bi-save me-1"></i> Save Payment');
                }
            });
        });

        // Clean up modal when closed
        $('#paymentModal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    }

    // Utility functions
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return isNaN(date) ? dateString : date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    function showAlert(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${escapeHtml(message)}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        $('.search-container').prepend(alertHtml);
        setTimeout(() => $('.alert').alert('close'), 5000);
    }
});