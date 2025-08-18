$(function() {
    function showSearchSection() {
        $("#accountDetails").addClass("hidden");
        $("#searchSection").removeClass("hidden");
        $("#search_account").val('').focus(); // Keeps search UX clean
        $("#addAccountContainer").addClass("hidden");
    }

    let typingTimer;
    let isAddMode = false;
    const doneTypingInterval = 500;

    // Changed from keyup to keydown to prevent form submission on enter
    $("#search_account").on("keydown", function(e) {
        if (e.keyCode === 13) { // Enter key
            e.preventDefault();
            performSearch();
            return;
        }

        clearTimeout(typingTimer);
        typingTimer = setTimeout(function() {
            searchAccount($("#search_account").val());
        }, doneTypingInterval);
    });

    // Search button click handler
    $("#searchButton").on("click", function(e) {
        e.preventDefault();
        performSearch();
    });

    // Close popup handlers
    $(".close-popup, #searchOverlay").on("click", function() {
        $("#searchResultsPopup, #searchOverlay").hide();
    });

    // Back to search button handler
    $("#backToSearch").on("click", function() {
        showSearchSection();
    });

    function performSearch() {
        const searchTerm = $("#search_account").val().trim();
        const timestamp = new Date().getTime();

        $("#searchResultsContainer").html('<div class="text-center p-3"><div class="spinner-border text-primary"></div></div>');
        $("#searchResultsPopup, #searchOverlay").show();

        $.ajax({
            url: searchUrl + "?term=" + encodeURIComponent(searchTerm) +
                 "&all=" + (searchTerm === "") + "&_=" + timestamp,
            dataType: "json",
            cache: false,
            beforeSend: function() {
                $("#searchResultsPopup").css('opacity', '0.8');
            },
            success: function(data) {
                if (!data || data.length === 0) {
                    showSearchResults([]);
                    return;
                }
                showSearchResults(data);
            },
            complete: function() {
                $("#searchResultsPopup").css('opacity', '1');
            }
        });
    }

    function showSearchResults(results) {
        const container = $("#searchResultsContainer");
        container.empty();

        if (results.length === 0) {
            container.append("<p>No results found</p>");
        } else {
            results.forEach(function(item) {
                const resultItem = $(`
                    <div class="result-item" data-account='${JSON.stringify(item.data).replace(/'/g, "&apos;")}'>
                        <strong>${item.label}</strong>
                        <div class="account-details">
                            ${item.data.service_provider} | ${item.data.category} | ${item.data.account_owner}
                        </div>
                    </div>
                `);

                // Attach click handler directly to this element
                resultItem.on("click", function() {
                    const accountData = JSON.parse($(this).attr("data-account").replace(/&apos;/g, "'"));
                    updateFormFields(accountData);
                    showAccountDetails(accountData);
                    $("#searchResultsPopup, #searchOverlay").hide();
                    $("#loadAddAccountForm").hide();
                });

                container.append(resultItem);
            });
        }

        $("#searchResultsPopup, #searchOverlay").show();
    }

    function searchAccount(term) {
        if (term.trim() === "") return;

        $.ajax({
            url: searchUrl,  // Use the variable here
            dataType: "json",
            data: { term: term },
            success: function(data) {
                $("#search_account").autocomplete("option", "source", data);
            },
            error: function(xhr, status, error) {
                console.error("AJAX error:", error);
            }
        });
    }

    function updateFormFields(data) {
        // Update hidden fields
        $("#service_provider").val(data.service_provider);
        $("#account_name").val(data.account_name);
        $("#account_number").val(data.account_number);
        $("#category").val(data.category);
        $("#paybill_number").val(data.paybill_number);
        $("#ussd_number").val(data.ussd_number);
        $("#frequency").val(data.frequency);
        $("#billing_date").val(data.billing_date);
        $("#bill_amount").val(data.bill_amount);
        $("#account_owner").val(data.account_owner);
        $("#invoice_number").val(data.invoice_number);
        $("#bank_account").val(data.bank_account);

        // Update editable form fields
        $("#edit-service_provider").val(data.service_provider);
        $("#edit-account_name").val(data.account_name);
        $("#edit-account_number").val(data.account_number);
        $("#edit-category").val(data.category);
        $("#edit-paybill_number").val(data.paybill_number);
        $("#edit-ussd_number").val(data.ussd_number);
        $("#edit-frequency").val(data.frequency);
        $("#edit-billing_date").val(data.billing_date);
        $("#edit-bill_amount").val(data.bill_amount);
        $("#edit-account_owner").val(data.account_owner);
        $("#edit-invoice_number").val($("#invoice_number").val());
        $("#edit-bank_account").val(data.bank_account);
    }

    function showAccountDetails(data) {
        $("#searchSection").addClass("hidden");
        $("#accountDetails").removeClass("hidden");
        $("#addAccountContainer").addClass("hidden");

        $("#view-service_provider").text(data.service_provider);
        $("#view-account_name").text(data.account_name);
        $("#view-account_number").text(data.account_number);
        $("#view-category").text(data.category);
        $("#view-paybill_number").text(data.paybill_number);
        $("#view-ussd_number").text(data.ussd_number);
        $("#view-frequency").text(data.frequency);
        $("#view-billing_date").text(data.billing_date);
        $("#view-bill_amount").text(data.bill_amount);
        $("#view-account_owner").text(data.account_owner);
        $("#view-invoice_number").text(data.invoice_number);
        $("#view-bank_account").text(data.bank_account);

        $("#viewAccountDetails").show();
        $("#editAccountForm").hide();

        $("#service_provider").val(data.service_provider);
        $("#account_name").val(data.account_name);
        $("#account_number").val(data.account_number);
        $("#category").val(data.category);
        $("#paybill_number").val(data.paybill_number);
        $("#ussd_number").val(data.ussd_number);
        $("#frequency").val(data.frequency);
        $("#billing_date").val(data.billing_date);
        $("#bill_amount").val(data.bill_amount);
        $("#account_owner").val(data.account_owner);
        $("#invoice_number").val(data.invoice_number);
        $("#bank_account").val(data.bank_account);
    }

    // Delete button handler
    $("#deleteAccountBtn").on("click", function(e) {
        e.preventDefault();

        const invoiceNumber = $("#view-invoice_number").text().trim();

        if (!invoiceNumber) {
            alert('Invoice number not found.');
            return;
        }

        if (!confirm(`Are you sure you want to delete the billing account with invoice number ${invoiceNumber}?`)) {
            return;
        }

        $.ajax({
            url: '/delete_billing_account',
            method: 'POST',
            data: {
                invoice_number: invoiceNumber
            },
            success: function(data) {
                if (data.success) {
                    alert(data.message);
                    $("#accountDetails").addClass("hidden");
                    $("#searchSection").removeClass("hidden");
                    // Optional: Clear search results
                    $("#search_account").val('');
                } else {
                    alert(`Error: ${data.message}`);
                }
            },
            error: function(xhr, status, error) {
                console.error('Delete failed:', error);
                alert('An error occurred. Please try again.');
            }
        });
    });

    // Edit button handler
    $("#editAccountBtn").on("click", function() {
        // Hide read-only view, show edit form
        $("#viewAccountDetails").hide();
        $("#editAccountForm").show();

        // Add editable class to all inputs except invoice number
        $("#editAccountForm input:not(#edit-invoice_number)").addClass("editable-field");
        $("#accountDetailsTitle").text("Edit Account Details");

        // Populate editable fields from hidden fields
        $("#edit-service_provider").val($("#service_provider").val());
        $("#edit-account_name").val($("#account_name").val());
        $("#edit-account_number").val($("#account_number").val());
        $("#edit-category").val($("#category").val());
        $("#edit-paybill_number").val($("#paybill_number").val());
        $("#edit-ussd_number").val($("#ussd_number").val());
        $("#edit-frequency").val($("#frequency").val());
        $("#edit-billing_date").val($("#billing_date").val());
        $("#edit-bill_amount").val($("#bill_amount").val());
        $("#edit-account_owner").val($("#account_owner").val());
        $("#edit-invoice_number").val($("#invoice_number").val());
        $("#edit-bank_account").val($("#bank_account").val());
    });

    // Cancel edit handler
    $("#cancelEdit").on("click", function() {
        // Show read-only view, hide edit form
        $("#viewAccountDetails").show();
        $("#editAccountForm").hide();
        $("#accountDetailsTitle").text("Account Details");
    });

    // Enhanced Form submission handler with improved success display
    $("#editAccountForm").on("submit", function(e) {
        e.preventDefault();

        const form = $(this);
        const submitBtn = form.find('button[type="submit"]');
        const originalBtnText = submitBtn.html();

        if (submitBtn.prop('disabled')) {
            return false;
        }

        // Show loading state
        submitBtn.prop('disabled', true).html(`
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...
        `);

        // Clear any existing alerts
        form.find('.alert').remove();

        $.ajax({
            url: form.attr('action'),
            type: 'POST',
            data: form.serialize(),
            dataType: 'json',
            timeout: 30000,
            success: function(response) {
                if (response.success) {
                    // Show success message with bill details similar to add form
                    let billsHtml = '';
                    if (response.generated_bills && response.generated_bills.length > 0) {
                        billsHtml = `
                            <div class="mt-3">
                                <h5>Generated Bills (${response.generated_bills.length}):</h5>
                                <div class="table-responsive">
                                    <table class="table table-sm table-striped">
                                        <thead class="thead-dark">
                                            <tr>
                                                <th>Due Date</th>
                                                <th>Amount</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${response.generated_bills.map(bill => `
                                                <tr>
                                                    <td>${bill.due_date}</td>
                                                    <td>${bill.amount}</td>
                                                    <td><span class="badge badge-primary">${bill.status}</span></td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        `;
                    }

                    // Replace the account details section with success message
                    $("#accountDetails").html(`
                        <div class="container-fluid">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h4>Account Updated Successfully</h4>
                                <button class="btn btn-secondary" id="backToEditSearch">
                                    <i class="fas fa-arrow-left"></i> Back to Search
                                </button>
                            </div>
                            <div class="alert alert-success">
                                <h5><i class="fas fa-check-circle"></i> Billing Account Updated Successfully!</h5>
                                </div>
                                ${billsHtml}
                            </div>
                        </div>
                    `);

                    // Set up the back to search button
                    $("#backToEditSearch").on("click", function() {
                        showSearchSection();
                    });

                } else {
                    showErrorAlert(response.message || 'Update failed');
                }
            },
            error: function(xhr, textStatus, errorThrown) {
                let errorMsg = 'Failed to update account';

                if (textStatus === 'timeout') {
                    errorMsg = 'Request timed out. Please try again.';
                } else {
                    try {
                        const errorResponse = JSON.parse(xhr.responseText);
                        errorMsg = errorResponse.message || errorMsg;
                    } catch (e) {
                        console.error('Error parsing response:', e);
                        if (xhr.status === 500) {
                            errorMsg = 'Server error occurred. Please check with administrator.';
                        } else if (xhr.status === 400) {
                            errorMsg = 'Invalid request. Please check your input data.';
                        }
                    }
                }
                showErrorAlert(errorMsg);
            },
            complete: function() {
                // Always re-enable the button
                submitBtn.html(originalBtnText).prop('disabled', false);
            }
        });
    });

    function showErrorAlert(message) {
        const alert = $(`
            <div class="alert alert-danger alert-dismissible fade show">
                <i class="fas fa-exclamation-triangle"></i> ${message}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `);
        $('#editAccountForm').prepend(alert);
        setTimeout(() => alert.alert('close'), 5000);
    }

    // When a result is clicked
    function loadEditForm(accountData) {
        $.post("{{ url_for('edit_billing_account') }}", accountData, function(html) {
            $("#accountDetails").html(html).removeClass("hidden");
            $("#searchResultsPopup, #searchOverlay").hide();

            // Update form fields with the data
            updateFormFields(accountData);
        });
    }

    // Replace the autocomplete initialization with:
    $("#search_account").autocomplete({
        minLength: 0,
        source: function(request, response) {
            // Your existing search logic
        }
    }).autocomplete("instance")._renderItem = function(ul, item) {
        return $("<li>")
            .append(`
                <div>
                    <strong>${item.label}</strong>
                    <div class="account-details">
                        ${item.data.service_provider} | ${item.data.category} | ${item.data.account_owner}
                    </div>
                </div>
            `)
            .appendTo(ul);
    };

    // Add New button handler
    $("#addBillingAcc").on("click", function(e) {
        e.preventDefault();
        loadAddAccountForm();
    });

    function getNextInvoiceNumber(callback) {
        $.ajax({
            url: '/get_next_invoice_number',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.invoice_number) {
                    callback(response.invoice_number);
                } else {
                    console.error('Failed to get invoice number');
                    callback('INV-ERROR'); // Fallback value
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching invoice number:', error);
                callback('INV-ERROR'); // Fallback value
            }
        });
    }

    function loadAddAccountForm() {
        // Hide popup and search section
        $("#searchResultsPopup, #searchOverlay").hide();
        $("#searchSection").addClass("hidden");

        // Show loading state
        $("#addAccountContainer").empty().removeClass("hidden").html(`
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4>Add New Billing Account</h4>
                <button class="btn btn-secondary" id="backToAddSearch">
                    <i class="fas fa-arrow-left"></i> Back to Search
                </button>
            </div>
            <div class="text-center p-3">
                <div class="spinner-border text-primary"></div>
                <p>Loading form...</p>
            </div>
        `);

        // Set up back button
        $("#backToAddSearch").on("click", showSearchSection);

        // Just load the form directly
        $.ajax({
            url: "/add_billing_account",
            type: "GET",
            success: function(data) {
                $("#addAccountContainer").html(data);

                //Generate and populate invoice number field
                getNextInvoiceNumber(function(invoiceNumber) {
                    $("#add-invoice_number").val(invoiceNumber);
                });

                setupAddFormHandlers();
            },
            error: function(xhr) {
                let errorMsg = "Failed to load form";
                if (xhr.status === 404) {
                    errorMsg = "Form template not found";
                }
                $("#addAccountContainer").html(`
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i> ${errorMsg}
                        <button class="btn btn-secondary mt-2" id="backToAddSearch">
                            <i class="fas fa-arrow-left"></i> Back to Search
                        </button>
                    </div>
                `);
                $("#backToAddSearch").on("click", showSearchSection);
            }
        });
    }

    function setupAddFormHandlers() {
        // Cancel/back button
        $("#cancelAdd, #backToAddSearch").on("click", showSearchSection);

        // Form submission
        $("#addAccountForm").on("submit", function(e) {
            e.preventDefault();
            saveNewAccount();
        });
    }

    function saveNewAccount() {
        const form = $("#addAccountForm");
        const submitBtn = form.find('button[type="submit"]');
        const originalBtnText = submitBtn.html();

        // Prevent multiple submissions
        if (submitBtn.prop('disabled')) {
            return false;
        }

        // Basic validation
        const requiredFields = ['service_provider', 'account_name', 'account_number', 'billing_date'];
        let hasErrors = false;

        form.find('.alert').remove(); // Clear existing alerts

        requiredFields.forEach(field => {
            const value = form.find(`[name="${field}"]`).val();
            if (!value || value.trim() === '') {
                hasErrors = true;
            }
        });

        if (hasErrors) {
            form.prepend(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> Please fill in all required fields
                </div>
            `);
            return false;
        }

        // Show loading state
        submitBtn.prop('disabled', true).html(`
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...
        `);

        // Get form data
        const formData = form.serialize();

        $.ajax({
            url: "/search_billing_account",
            type: "POST",
            data: formData,
            dataType: 'json', // Explicitly expect JSON response
            timeout: 30000,
            success: function(response) {
                if (response.success) {
                    // Show success message with bill details
                    let billsHtml = '';
                    if (response.generated_bills && response.generated_bills.length > 0) {
                        billsHtml = `
                            <div class="mt-3">
                                <h5>Generated Bills (${response.generated_bills.length}):</h5>
                                <div class="table-responsive">
                                    <table class="table table-sm table-striped">
                                        <thead class="thead-dark">
                                            <tr>
                                                <th>Due Date</th>
                                                <th>Amount</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${response.generated_bills.map(bill => `
                                                <tr>
                                                    <td>${bill.due_date}</td>
                                                    <td>${bill.amount}</td>
                                                    <td><span class="badge badge-primary">${bill.status}</span></td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        `;
                    }

                    $("#addAccountContainer").html(`
                        <div class="container-fluid">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h4>Account Created Successfully</h4>
                                <button class="btn btn-secondary" id="backToAddSearch">
                                    <i class="fas fa-arrow-left"></i> Back to Search
                                </button>
                            </div>
                            <div class="alert alert-success">
                                <h5><i class="fas fa-check-circle"></i> Billing Account Created Successfully!</h5>
                                <p><strong>Invoice Number:</strong> ${response.invoice_number}</p>
                                <p><strong>Created on:</strong> ${response.created_date}</p>
                                ${billsHtml}
                            </div>
                        </div>
                    `);

                    $("#backToAddSearch").on("click", showSearchSection);
                } else {
                    // Show error message
                    $("#addAccountContainer").prepend(`
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle"></i> ${response.message}
                        </div>
                    `);
                    submitBtn.html(originalBtnText).prop('disabled', false);
                }
            },
            error: function(xhr, textStatus, errorThrown) {
                console.error('AJAX Error:', xhr.status, xhr.statusText, textStatus);
                console.error('Response:', xhr.responseText);

                let errorMessage = "An error occurred while saving the account";

                if (textStatus === 'timeout') {
                    errorMessage = "Request timed out. The account may have been created. Please check and try again if needed.";
                } else {
                    try {
                        const errorResponse = JSON.parse(xhr.responseText);
                        if (errorResponse.message) {
                            errorMessage = errorResponse.message;
                        }
                    } catch (e) {
                        // If response is not JSON, use default message
                        if (xhr.status === 500) {
                            errorMessage = "Server error occurred. Please check the server logs.";
                        } else if (xhr.status === 400) {
                            errorMessage = "Invalid request. Please check your input data.";
                        }
                    }
                }

                $("#addAccountContainer").prepend(`
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i> ${errorMessage}
                    </div>
                `);
                submitBtn.html(originalBtnText).prop('disabled', false);
            }
        });
    }
});