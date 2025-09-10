$(function() {
    function showSearchSection() {
        $("#supplierDetails").addClass("hidden");
        $("#addSupplierContainer").addClass("hidden");
        $("#searchSection").removeClass("hidden");
        $("#search_supplier").val('').focus(); // Keeps search UX clean
    }

    let typingTimer;
    let isAddMode = false;
    const doneTypingInterval = 500;

    // Changed from keyup to keydown to prevent form submission on enter
    $("#search_supplier").on("keydown", function(e) {
        if (e.keyCode === 13) { // Enter key
            e.preventDefault();
            performSearch();
            return;
        }

        clearTimeout(typingTimer);
        typingTimer = setTimeout(function() {
            searchSupplier($("#search_supplier").val());
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
        const searchTerm = $("#search_supplier").val().trim();
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
                    <div class="result-item" data-supplier='${JSON.stringify(item.data).replace(/'/g, "&apos;")}'>
                        <strong>${item.label}</strong>
                        <div class="supplier-details">
                           ${item.data.contact_name} | ${item.data.telephone}
                        </div>
                    </div>
                `);
            });
        }

        // Add click handler for result items
        $(".result-item").on("click", function() {
            const supplierData = JSON.parse($(this).attr("data-supplier").replace(/&apos;/g, "'"));
            updateFormFields(supplierData);
            showSupplierDetails(supplierData); // Pass the data here
            $("#searchResultsPopup, #searchOverlay").hide();
        });

        $("#searchResultsPopup, #searchOverlay").show();
    }

    function searchSupplier(term) {
        if (term.trim() === "") return;

        $.ajax({
            url: searchUrl,  // Use the variable here
            dataType: "json",
            data: { term: term },
            success: function(data) {
                $("#search_supplier").autocomplete("option", "source", data);
            },
            error: function(xhr, status, error) {
                console.error("AJAX error:", error);
            }
        });
    }

    function updateFormFields(data) {
        // Update hidden fields
        $("#supplier_id").val(data.supplier_id);
        $("#supplier_name").val(data.supplier_name);
        $("#contact_name").val(data.contact_name);
        $("#telephone").val(data.telephone);
        $("#email").val(data.email);
        $("#created_at").val(data.created_at);
        $("#updated_at").val(data.updated_at);

        // Update editable form fields
        $("#edit-supplier_id").val(data.supplier_id);
        $("#edit-supplier_name").val(data.supplier_name);
        $("#edit-contact_name").val(data.contact_name);
        $("#edit-telephone").val(data.telephone);
        $("#edit-email").val(data.email);
    }

    function showSupplierDetails(data) {
        $("#searchSection").addClass("hidden");
        $("#addSupplierContainer").addClass("hidden");
        $("#supplierDetails").removeClass("hidden");

        $("#view-supplier_id").text(data.supplier_id);
        $("#view-supplier_name").text(data.supplier_name);
        $("#view-contact_name").text(data.contact_name);
        $("#view-telephone").text(data.telephone);
        $("#view-email").text(data.email);
        $("#view-created_at").text(data.created_at);
        $("#view-updated_at").text(data.updated_at);

        $("#viewSupplierDetails").show();
        $("#editSupplierForm").hide();

        $("#supplier_id").val(data.supplier_id);
        $("#supplier_name").val(data.supplier_name);
        $("#contact_name").val(data.contact_name);
        $("#telephone").val(data.telephone);
        $("#email").val(data.email);
        $("#created_at").val(data.created_at);
        $("#updated_at").val(data.updated_at);
    }

    // Edit button handler
    $("#editSupplierBtn").on("click", function() {
        // Hide read-only view, show edit form
        $("#viewSupplierDetails").hide();
        $("#editSupplierForm").show();

        // Add editable class to all inputs except supplier_id
        $("#editSupplierForm input:not(#edit-supplier_id)").addClass("editable-field");
        $("#supplierDetailsTitle").text("Edit Supplier Details");

        // Populate editable fields from hidden fields
        $("#edit-supplier_id").val($("#supplier_id").val());
        $("#edit-supplier_name").val($("#supplier_name").val());
        $("#edit-contact_name").val($("#contact_name").val());
        $("#edit-telephone").val($("#telephone").val());
        $("#edit-email").val($("#email").val());
    });

    // Cancel edit handler
    $("#cancelEdit").on("click", function() {
        // Show read-only view, hide edit form
        $("#viewSupplierDetails").show();
        $("#editSupplierForm").hide();
        $("#supplierDetailsTitle").text("Supplier Details");
    });

    // Form submission handler with loader
    $("#editSupplierForm").on("submit", function(e) {
        e.preventDefault();

        // Show loading indicator on edit form
        const submitBtn = $(this).find('button[type="submit"]');
        const originalBtnText = submitBtn.html();
        submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...');

        // Collect form data
        const formData = $(this).serialize() + '&supplier_id=' + encodeURIComponent($("#supplier_id").val());
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
                    supplier_id: $("#supplier_id").val(),
                    supplier_name: $("#edit-supplier_name").val(),
                    contact_name: $("#edit-contact_name").val(),
                    telephone: $("#edit-telephone").val(),
                    email: $("#edit-email").val(),
                    created_at: $("#created_at").val(),
                    updated_at: new Date().toISOString(),
                };

                showSupplierDetails(updatedData);

                // Reset button after 2 seconds
                setTimeout(() => {
                    submitBtn.html(originalBtnText).removeClass('btn-success').addClass('btn-primary').prop('disabled', false);
                    $("#viewSupplierDetails").show();
                    $("#editSupplierForm").hide();
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
    function loadEditForm(supplierData) {
        $.post("{{ url_for('edit_supplier') }}", supplierData, function(html) {
            $("#supplierDetails").html(html).removeClass("hidden");
            $("#searchResultsPopup, #searchOverlay").hide();

            // Update form fields with the data
            updateFormFields(supplierData);
        });
    }

    // Initialize autocomplete
    $("#search_supplier").autocomplete({
        minLength: 0, // Show suggestions even when empty
        select: function(event, ui) {
            updateFormFields(ui.item.data);
            showSupplierDetails();
            return false;
        }
    }).autocomplete("instance")._renderItem = function(ul, item) {
        return $("<li>")
            .append(`
                <div>
                    <strong>${item.label}</strong>
                    <div class="supplier-details">
                        ${item.data.contact_name} | ${item.data.telephone}
                    </div>
                </div>
            `)
            .appendTo(ul);
    };

    // Add New button handler
    $("#addSupplier").on("click", function(e) {
        e.preventDefault();
        loadAddSupplierForm();
    });

    function loadAddSupplierForm() {
        // Hide popup and search section
        $("#searchResultsPopup, #searchOverlay").hide();
        $("#searchSection").addClass("hidden");
        $("#supplierDetails").addClass("hidden");
        // Show loading state
        $("#addSupplierContainer").empty().removeClass("hidden").html(`
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4>Add New Supplier</h4>
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
            url: "/add_supplier",
            type: "GET",
            success: function(data) {
                $("#addSupplierContainer").html(data);
                setupAddFormHandlers();
            },
            error: function(xhr) {
                let errorMsg = "Failed to load form";
                if (xhr.status === 404) {
                    errorMsg = "Form template not found";
                }
                $("#addSupplierContainer").html(`
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

        // Form submission with loader
        $("#addSupplierForm").on("submit", function(e) {
            e.preventDefault();

            // Show loading indicator on add form
            const submitBtn = $(this).find('button[type="submit"]');
            const originalBtnText = submitBtn.html();
            submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...');

            saveNewSupplier(submitBtn, originalBtnText);
        });
    }

    function saveNewSupplier(submitBtn, originalBtnText) {
        const formData = $("#addSupplierForm").serialize();

        $.ajax({
            url: "/suppliers",
            type: "POST",
            data: formData,
            success: function(response) {
                if (response.success) {
                    // Show success state on button
                    submitBtn.html('<i class="fas fa-check"></i> Saved!').removeClass('btn-primary').addClass('btn-success');

                    $("#addSupplierContainer").html(`
                        <div class="alert alert-success">
                            ${response.message}<br>
                            <strong>Supplier Name:</strong> ${response.supplier_name}<br>
                            <strong>Created on:</strong> ${response.created_at}
                        </div>
                        <button class="btn btn-secondary mt-3" id="backToAddSearch">Back to Search</button>
                    `);
                    $("#backToAddSearch").on("click", showSearchSection);

                    // Reset button after 2 seconds
                    setTimeout(() => {
                        submitBtn.html(originalBtnText).removeClass('btn-success').addClass('btn-primary').prop('disabled', false);
                    }, 2000);
                } else {
                    submitBtn.html(originalBtnText).prop('disabled', false);
                    $("#addSupplierContainer").prepend(`
                        <div class="alert alert-danger">${response.message}</div>
                    `);
                }
            },
            error: function(xhr) {
                submitBtn.html(originalBtnText).prop('disabled', false);
                $("#addSupplierContainer").prepend(`
                    <div class="alert alert-danger">
                        Server error: ${xhr.responseText}
                    </div>
                `);
            }
        });
    }

    // Delete button handler with loader
    document.getElementById('deleteSupplierBtn').addEventListener('click', function () {
        const supplierId = document.getElementById('supplier_id').value;
        const deleteBtn = this;

        if (!supplierId) {
            alert("No supplier selected.");
            return;
        }

        if (!confirm("Are you sure you want to delete this supplier?")) {
            return;
        }

        // Show loading state on delete button
        const originalBtnText = deleteBtn.innerHTML;
        deleteBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';
        deleteBtn.disabled = true;

        fetch("/suppliers", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                form_type: 'delete',
                supplier_id: supplierId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success state on button
                deleteBtn.innerHTML = '<i class="fas fa-check"></i> Deleted!';
                deleteBtn.classList.remove('btn-danger');
                deleteBtn.classList.add('btn-success');

                setTimeout(() => {
                    alert("Supplier deleted successfully.");
                    showSearchSection();
                    // Reset button after action completes
                    deleteBtn.innerHTML = originalBtnText;
                    deleteBtn.classList.remove('btn-success');
                    deleteBtn.classList.add('btn-danger');
                    deleteBtn.disabled = false;
                }, 1000);
            } else {
                deleteBtn.innerHTML = originalBtnText;
                deleteBtn.disabled = false;
                alert("Error deleting supplier: " + data.message);
            }
        })
        .catch(error => {
            deleteBtn.innerHTML = originalBtnText;
            deleteBtn.disabled = false;
            alert("An error occurred while deleting the supplier.");
            console.error(error);
        });
    });
}); // This closes the main jQuery function