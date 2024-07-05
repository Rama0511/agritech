$(document).ready(function() {
    $('#customerTable').DataTable();
  });

  function runMain() {
    $.ajax({
      url: 'run_main.php',
      type: 'GET',
      success: function(response) {
        alert('main.py executed successfully!');
        // You can handle additional actions here based on response
      },
      error: function() {
        alert('Error running main.py.');
      }
    });
  }