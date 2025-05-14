$(document).ready(function() {
  // Initialize datepicker for start_date and end_date
  $("#start_date, #end_date").datepicker({
    dateFormat: "dd-mm-yy",
    changeMonth: true,
    changeYear: true,
    showButtonPanel: true
  });

  // Set default start date to 2 years from today
  var startDate = new Date();
  startDate.setFullYear(startDate.getFullYear() - 2); // Set 2 years before today
  $("#start_date").datepicker("setDate", startDate);

  // Set default end date to 1 week from today
  var endDate = new Date();
  endDate.setDate(endDate.getDate() + 7); // Set 1 week ahead from today
  $("#end_date").datepicker("setDate", endDate);

  // Optional: Format the dates if you want to show them in a different format
  // $("#start_date").val($.datepicker.formatDate('yy-mm-dd', startDate));
  // $("#end_date").val($.datepicker.formatDate('yy-mm-dd', endDate));

  // Example: Handle form submission
  $('#filter-form').on('submit', function(e) {
    e.preventDefault();
    // your AJAX code or filter logic here
  });
});
