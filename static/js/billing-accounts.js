$(function() {
    function showSearchSection() {
        $("#accountDetails").addClass("hidden");
        $("#searchSection").removeClass("hidden");
        $("#search_account").val('').focus(); // Keeps search UX clean
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
                container.append(`
                    <div class="result-item" data-account='${JSON.stringify(item.data).replace(/'/g, "&apos;")}'>
                        <strong>${item.label}</strong>
                        <div class="account-details">
                            ${item.data.service_provider} | ${item.data.category} | ${item.data.account_owner}
                        </div>
                    </div>
                `);
            });
        }

        // Add click handler for result items
        $(".result-item").on("click", function() {
            const accountData = JSON.parse($(this).attr("data-account").replace(/&apos;/g, "'"));
            updateFormFields(accountData);
            showAccountDetails(accountData); // Pass the data here
            $("#searchResultsPopup, #searchOverlay").hide();
        });

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

    // Form submission handler remains the same
    $("#editAccountForm").on("submit", function(e) {
        e.preventDefault();

        // Show loading indicator
        const submitBtn = $(this).find('button[type="submit"]');
        const originalBtnText = submitBtn.html();
        submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...');

        // Collect form data
        const formData = $(this).serialize();

        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            success: function(response) {
                // Show success message
                submitBtn.html('<i class="fas fa-check"></i> Saved!').removeClass('btn-primary').addClass('btn-success');

                // Create a temporary success message
                const successAlert = $(`
                    <div class="alert alert-success alert-dismissible fade show" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 1000;">
                        <strong>Success!</strong> Changes saved successfully.
                        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                `);

                // Add to body and auto-dismiss after 3 seconds
                $('body').append(successAlert);
                setTimeout(() => {
                    successAlert.alert('close');
                }, 3000);

                // Update the view with new data
                const updatedData = {
                    service_provider: $("#edit-service_provider").val(),
                    account_name: $("#edit-account_name").val(),
                    account_number: $("#edit-account_number").val(),
                    category: $("#edit-category").val(),
                    paybill_number: $("#edit-paybill_number").val(),
                    ussd_number: $("#edit-ussd_number").val(),
                    frequency: $("#edit-frequency").val(),
                    billing_date: $("#edit-billing_date").val(),
                    bill_amount: $("#edit-bill_amount").val(),
                    account_owner: $("#edit-account_owner").val(),
                    invoice_number: $("#edit-invoice_number").val(),
                    bank_account: $("#edit-bank_account").val()
                };

                showAccountDetails(updatedData);

                // Reset button after 2 seconds
                setTimeout(() => {
                    submitBtn.html(originalBtnText).removeClass('btn-success').addClass('btn-primary').prop('disabled', false);
                    $("#viewAccountDetails").show();
                    $("#editAccountForm").hide();
                }, 2000);
            },
            error: function(xhr) {
                // Handle error
                submitBtn.html(originalBtnText).removeClass('btn-success').addClass('btn-primary').prop('disabled', false);

                const errorAlert = $(`
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <strong>Error!</strong> Failed to save changes. Please try again.
                        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                `);

                $('body').append(errorAlert);
                setTimeout(() => {
                    errorAlert.alert('close');
                }, 3000);
            }
        });
    });

    // When a result is clicked
    function loadEditForm(accountData) {
        $.post("{{ url_for('edit_billing_account') }}", accountData, function(html) {
            $("#accountDetails").html(html).removeClass("hidden");
            $("#searchResultsPopup, #searchOverlay").hide();

            // Update form fields with the data
            updateFormFields(accountData);
        });
    }

    // Initialize autocomplete
    $("#search_account").autocomplete({
        minLength: 0, // Show suggestions even when empty
        select: function(event, ui) {
            updateFormFields(ui.item.data);
            showAccountDetails();
            return false;
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

    function loadAddAccountForm() {
        // Hide popup and search section
        $("#searchResultsPopup, #searchOverlay").hide();
        $("#searchSection").addClass("hidden");

        // Show loading state
        $("#accountDetails").empty().removeClass("hidden").html(`
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

        // Load form via AJAX
        $.ajax({
            url: "/add_billing_account",
            type: "GET",
            success: function(data) {
                $("#accountDetails").html(data);
                setupAddFormHandlers();
            },
            error: function(xhr) {
                let errorMsg = "Failed to load form";
                if (xhr.status === 404) {
                    errorMsg = "Form template not found";
                }
                $("#accountDetails").html(`
                    <div class="alert alert-danger">
                        ${errorMsg}
                        <button class="btn btn-secondary mt-2" id="backToAddSearch">
                            Back to Search
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
        const formData = $("#addAccountForm").serialize(); // Serializes form into URL-encoded string

        $.ajax({
            url: "/search_billing_account",
            type: "POST",
            data: formData,
            success: function(response) {
                if (response.success) {
                    $("#accountDetails").html(`
                        <div class="alert alert-success">
                            ${response.message}<br>
                            <strong>Invoice #:</strong> ${response.invoice_number}<br>
                            <strong>Created on:</strong> ${response.created_date}
                        </div>
                        <button class="btn btn-secondary mt-3" id="backToAddSearch">Back to Search</button>
                    `);
                    $("#backToAddSearch").on("click", showSearchSection);
                } else {
                    $("#accountDetails").prepend(`
                        <div class="alert alert-danger">${response.message}</div>
                    `);
                }
            },
            error: function(xhr) {
                $("#accountDetails").prepend(`
                    <div class="alert alert-danger">
                        Server error: ${xhr.responseText}
                    </div>
                `);
            }
        });
    }
}); // This closes the main jQuery function