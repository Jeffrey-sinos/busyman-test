$(document).ready(function() {
  $('.loader').hide();
  // Initialize datepicker with dd/mm/yy format
  $("#start_date, #end_date").datepicker({
    dateFormat: "dd/mm/yy",
    changeMonth: true,
    changeYear: true,
    showButtonPanel: true
  });

  // Set default dates
  $("#start_date").datepicker("setDate", "-2y"); // 2 years ago
  $("#end_date").datepicker("setDate", "+7d");  // 1 week from today

  $('#filter-form').on('submit', function(e) {
    e.preventDefault();
    searchBills();
  });

  // Handle edit button clicks (delegated for dynamic content)
  $(document).on('click', '.edit-btn', function() {
    var billId = $(this).data('id');
    window.location.href = `/edit-bill/${billId}`;
  });
  // Add button is clicked
  $(document).on('click', '.add-btn', function() {
    window.location.href = `/add-bill`;
  });
  // Handle delete button clicks
  $(document).on('click', '.delete-btn', function() {
    var billId = $(this).data('id');
    deleteBill(billId);
  });
});

function searchBills() {
   $('.loader').show();
   $('#results-body').html('');
  // Get dates in yyyy-mm-dd format for backend
  var start_date = $.datepicker.formatDate('yy-mm-dd',
                $("#start_date").datepicker("getDate"));
  var end_date = $.datepicker.formatDate('yy-mm-dd',
              $("#end_date").datepicker("getDate"));

  var formData = {
    category: $('#category').val(),
    account_owner: $('#account_owner').val(),
    start_date: start_date,
    end_date: end_date
  };

  $.ajax({
    url: '/search-bills',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(formData),
    success: function(data) {
      if (data.error) {
        showError(data.error);
        return;
      }

      var rows = '';
      $.each(data, function(i, bill) {
        rows += `<tr data-id="${bill.bill_id}">
          <td>${bill.account_name || ''}</td>
          <td>${bill.account_number || ''}</td>
          <td>${bill.billing_date || ''}</td>
          <td>${bill.bill_amount || ''}</td>
          <td class="action-buttons">
            <div class="btn-group" role="group">
              <button class="btn btn-sm btn-primary edit-btn mr-3" data-id="${bill.bill_id}">
                 Edit
              </button>
              <button class="btn btn-sm btn-danger delete-btn" data-id="${bill.bill_id}">
                Delete
              </button>
            </div>
          </td>
        </tr>`;
      });
      $('#results-body').html(rows || '<tr><td colspan="5">No results found</td></tr>');
    },
    error: function(xhr) {
      showError(xhr.responseJSON?.error || 'Server error');
    },
    complete: function() {
      $('.loader').hide();
    }
  });
}

function deleteBill(billId) {
  if (!confirm('Are you sure you want to delete this bill?')) {
    return;
  }

  $.ajax({
    url: `/delete-bill/${billId}`,
    type: 'DELETE',
    success: function(response) {
      if (response.error) {
        showError(response.error);
        return;
      }

      // Remove the row from the table
      $(`tr[data-id="${billId}"]`).remove();
      showToast('Bill deleted successfully');
    },
    error: function(xhr) {
      showError(xhr.responseJSON?.error || 'Failed to delete bill');
    }
  });
}

function showError(message) {
  $('#results-body').html(`<tr><td colspan="5" class="text-danger">${message}</td></tr>`);
}

function showToast(message) {
  // Implement your toast notification or use:
  alert(message); // Simple fallback
}

$(document).ready(function() {
    // Load the invoice number automatically
    getNextInvoiceNumber();
    // Handle add bill form submission
    $('#addBillForm').on('submit', function(e) {
        e.preventDefault();

        // Get form data
        var formData = $(this).serialize();

        $.ajax({
            url: '/add-bills',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.error) {
                    alert('Error: ' + response.error);
                } else {
                    alert('Bill added successfully!');
                    // Redirect back to search page or clear form
                    window.location.href = '/search-bill';
                    // Or clear the form to add another:
                    // $('#addBillForm')[0].reset();
                }
            },
            error: function(xhr) {
                alert('Error: ' + (xhr.responseJSON?.error || 'Server error'));
            }
        });
    });

    // Handle cancel button
    $('#cancelAdd').on('click', function() {
        window.location.href = '/search-bill';
    });

    // Handle back to search button (if it exists)
    $('#backToAddSearch').on('click', function() {
        window.location.href = '/search-bill';
    });
});
function getNextInvoiceNumber() {
    $.ajax({
        url: '/get_next_invoice_number',
        type: 'GET',
        success: function(response) {
            if (response.invoice_number) {
                $('#add-invoice_number').val(response.invoice_number);
            }
        },
        error: function(xhr) {
            console.error('Failed to load invoice number:', xhr.responseJSON?.error || 'Server error');
            // Set a fallback invoice number
            var fallback = 'INV' + new Date().getTime();
            $('#add-invoice_number').val(fallback);
        }
    });
}

function validateAddBillForm() {
    var requiredFields = ['service_provider', 'account_name', 'account_number', 'category', 'billing_date', 'bill_amount'];
    var isValid = true;

    requiredFields.forEach(function(field) {
        var value = $('#add-' + field).val();
        if (!value || value.trim() === '') {
            $('#add-' + field).addClass('is-invalid');
            isValid = false;
        } else {
            $('#add-' + field).removeClass('is-invalid');
        }
    });

    return isValid;
}
