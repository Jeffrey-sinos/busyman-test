$(document).ready(function() {
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
          rows += `<tr>
            <td>${bill.account_name || ''}</td>
            <td>${bill.account_number || ''}</td>
            <td>${bill.billing_date || ''}</td>
            <td>${bill.bill_amount || ''}</td>
          </tr>`;
        });
        $('#results-body').html(rows || '<tr><td colspan="5">No results found</td></tr>');
      },
      error: function(xhr) {
        showError(xhr.responseJSON?.error || 'Server error');
      }
    });
  });
});

function showError(message) {
  $('#results-body').html(`<tr><td colspan="5" class="text-danger">${message}</td></tr>`);
}