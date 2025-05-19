$(function() {
    function showSearchSection() {
        $("#productDetails").addClass("hidden");
        $("#searchSection").removeClass("hidden");
        $("#search_product").val('').focus(); // Keeps search UX clean
    }

    let typingTimer;
    let isAddMode = false;
    const doneTypingInterval = 500;

    // Changed from keyup to keydown to prevent form submission on enter
    $("#search_product").on("keydown", function(e) {
        if (e.keyCode === 13) { // Enter key
            e.preventDefault();
            performSearch();
            return;
        }

        clearTimeout(typingTimer);
        typingTimer = setTimeout(function() {
            searchProduct($("#search_product").val());
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
    const searchTerm = $("#search_product").val().trim();
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
                    <div class="result-item" data-product='${JSON.stringify(item.data).replace(/'/g, "&apos;")}'>
                        <strong>${item.label}</strong>
                        <div class="product-details">
                           ${item.data.edition} | ${item.data.isbn}
                        </div>
                    </div>
                `);
            });
        }

        // Add click handler for result items
        $(".result-item").on("click", function() {
            const productData = JSON.parse($(this).attr("data-product").replace(/&apos;/g, "'"));
            updateFormFields(productData);
            showProductDetails(productData); // Pass the data here
            $("#searchResultsPopup, #searchOverlay").hide();
        });

        $("#searchResultsPopup, #searchOverlay").show();
    }

    function searchProduct(term) {
    if (term.trim() === "") return;

    $.ajax({
        url: searchUrl,  // Use the variable here
        dataType: "json",
        data: { term: term },
        success: function(data) {
            $("#search_product").autocomplete("option", "source", data);
        },
        error: function(xhr, status, error) {
            console.error("AJAX error:", error);
        }
    });
}

    function updateFormFields(data) {
        // Update hidden fields
        $("#product_number").val(data.product_number);
        $("#product").val(data.product);
        $("#edition").val(data.edition);
        $("#isbn").val(data.isbn);
        $("#date_published").val(data.date_published);
        $("#publisher").val(data.publisher);
        $("#author").val(data.author);
        $("#date_created").val(data.date_created);

        // Update editable form fields
        $("#edit-product_number").val($("#product_number").val());
        $("#edit-product").val(data.product);
        $("#edit-edition").val(data.edition);
        $("#edit-isbn").val(data.isbn);
        $("#edit-date_published").val(data.date_published);
        $("#edit-publisher").val(data.publisher);
        $("#edit-author").val(data.author);
        $("#edit-date_created").val(data.date_created);
        $("#edit-frequency").val(data.frequency);
    }

    function showProductDetails(data) {
        $("#searchSection").addClass("hidden");
        $("#productDetails").removeClass("hidden");

        $("#view-product_number").text(data.product_number);
        $("#view-product").text(data.product);
        $("#view-edition").text(data.edition);
        $("#view-isbn").text(data.isbn);
        $("#view-date_published").text(data.date_published);
        $("#view-publisher").text(data.publisher);
        $("#view-author").text(data.author);
        $("#view-date_created").text(data.date_created);
        $("#view-frequency").text(data.frequency);

        $("#viewProductDetails").show();
        $("#editProductForm").hide();

        $("#product_number").val(data.product_number);
        $("#product").val(data.product);
        $("#edition").val(data.edition);
        $("#isbn").val(data.isbn);
        $("#date_published").val(data.date_published);
        $("#publisher").val(data.publisher);
        $("#author").val(data.author);
        $("#date_created").val(data.date_created);
        $("#frequency").val(data.frequency);
    }

    // Edit button handler
    $("#editProductBtn").on("click", function() {
        // Hide read-only view, show edit form
        $("#viewProductDetails").hide();
        $("#editProductForm").show();

        // Add editable class to all inputs except invoice number
        $("#editProductForm input:not(#edit-product_number)").addClass("editable-field");
        $("#productDetailsTitle").text("Edit Product Details");

        // Populate editable fields from hidden fields
        $("#edit-product_number").val($("#product_number").val());
        $("#edit-product").val($("#product").val());
        $("#edit-edition").val($("#edition").val());
        $("#edit-isbn").val($("#isbn").val());
        $("#edit-date_published").val($("#date_published").val());
        $("#edit-publisher").val($("#publisher").val());
        $("#edit-author").val($("#author").val());
        $("#edit-date_created").val($("#date_created").val());
        $("#edit-frequency").val($("#frequency").val());
    });

    // Cancel edit handler
    $("#cancelEdit").on("click", function() {
        // Show read-only view, hide edit form
        $("#viewProductDetails").show();
        $("#editProductForm").hide();
        $("#productDetailsTitle").text("Product Details");
    });

    // Form submission handler remains the same
    $("#editProductForm").on("submit", function(e) {
        e.preventDefault();

        // Show loading indicator
        const submitBtn = $(this).find('button[type="submit"]');
        const originalBtnText = submitBtn.html();
        submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...');

        // Collect form data
        const formData = $(this).serialize() + '&product_number=' + encodeURIComponent($("#product_number").val());
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
                    product_number: $("#product_number").val(),
                    product: $("#edit-product").val(),
                    edition: $("#edit-edition").val(),
                    isbn: $("#edit-isbn").val(),
                    date_published: $("#edit-date_published").val(),
                    publisher: $("#edit-publisher").val(),
                    author: $("#edit-author").val(),
                    date_created: $("#edit-date_created").val(),
                    frequency: $("#edit-frequency").val(),
                };

                showProductDetails(updatedData);

                // Reset button after 2 seconds
                setTimeout(() => {
                    submitBtn.html(originalBtnText).removeClass('btn-success').addClass('btn-primary').prop('disabled', false);
                    $("#viewProductDetails").show();
                    $("#editProductForm").hide();
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
    function loadEditForm(productData) {
        $.post("{{ url_for('edit_product') }}", productData, function(html) {
            $("#productDetails").html(html).removeClass("hidden");
            $("#searchResultsPopup, #searchOverlay").hide();

            // Update form fields with the data
            updateFormFields(productData);
        });
    }

    // Initialize autocomplete
    $("#search_product").autocomplete({
        minLength: 0, // Show suggestions even when empty
        select: function(event, ui) {
            updateFormFields(ui.item.data);
            showProductDetails();
            return false;
        }
    }).autocomplete("instance")._renderItem = function(ul, item) {
        return $("<li>")
            .append(`
                <div>
                    <strong>${item.label}</strong>
                    <div class="product-details">
                        ${item.data.edition} | ${item.isbn}
                    </div>
                </div>
            `)
            .appendTo(ul);
    };

    // Add New button handler
    $("#addProduct").on("click", function(e) {
        e.preventDefault();
        loadAddProductForm();
    });

    function loadAddProductForm() {
        // Hide popup and search section
        $("#searchResultsPopup, #searchOverlay").hide();
        $("#searchSection").addClass("hidden");
        $("#productDetails").removeClass("hidden");
        // Show loading state
        $("#productDetails").empty().removeClass("hidden").html(`
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4>Add New Product</h4>
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
            url: "/add_product",
            type: "GET",
            success: function(data) {
                $("#productDetails").html(data);
                setupAddFormHandlers();
            },
            error: function(xhr) {
                let errorMsg = "Failed to load form";
                if (xhr.status === 404) {
                    errorMsg = "Form template not found";
                }
                $("#productDetails").html(`
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
        $("#addProductForm").on("submit", function(e) {
            e.preventDefault();
            saveNewProduct();
        });
    }

    function saveNewProduct() {
        const formData = $("#addProductForm").serialize(); // Serializes form into URL-encoded string

        $.ajax({
            url: "/products",
            type: "POST",
            data: formData,
            success: function(response) {
                if (response.success) {
                    $("#productDetails").html(`
                        <div class="alert alert-success">
                            ${response.message}<br>
                            <strong>Product Name:</strong> ${response.product}<br>
                            <strong>Created on:</strong> ${response.date_created}
                        </div>
                        <button class="btn btn-secondary mt-3" id="backToAddSearch">Back to Search</button>
                    `);
                    $("#backToAddSearch").on("click", showSearchSection);
                } else {
                    $("#productDetails").prepend(`
                        <div class="alert alert-danger">${response.message}</div>
                    `);
                }
            },
            error: function(xhr) {
                $("#productDetails").prepend(`
                    <div class="alert alert-danger">
                        Server error: ${xhr.responseText}
                    </div>
                `);
            }
        });
    }
    document.getElementById('deleteProductBtn').addEventListener('click', function () {
        const productNumber = document.getElementById('product_number').value;

        if (!productNumber) {
            alert("No product selected.");
            return;
        }

        if (!confirm("Are you sure you want to delete this product?")) {
            return;
        }

        fetch("/products", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                form_type: 'delete',
                product_number: productNumber
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Product deleted successfully.");
                showSearchSection();
            } else {
                alert("Error deleting product: " + data.message);
            }
        })
        .catch(error => {
            alert("An error occurred while deleting the product.");
            console.error(error);
        });
    });
}); // This closes the main jQuery function