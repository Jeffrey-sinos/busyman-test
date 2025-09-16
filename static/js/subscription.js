document.addEventListener('DOMContentLoaded', function() {
    // Check subscription status via AJAX
    fetch('/check_subscription_status')
        .then(response => response.json())
        .then(data => {
            if (!data.active) {
                showSubscriptionModal();
            }
        })
        .catch(error => {
            console.error('Error checking subscription status:', error);
        });

    function showSubscriptionModal() {
        // Show modal on page load
        $('#subscriptionModal').modal({
            backdrop: 'static',
            keyboard: false
        });

        // Handle payment form submission
        $('#paymentForm').on('submit', function(e) {
            e.preventDefault();

            const phoneNumber = $('#phoneNumber').val();
            const productId = $('#productSelect').val();

            // Show processing message
            $('#paymentForm').hide();
            $('#paymentStatus').show();

            // Initiate payment
            fetch('/initiate_payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    phone_number: phoneNumber,
                    product_id: productId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Poll for payment status
                    checkPaymentStatus(data.checkout_request_id);
                } else {
                    $('#paymentStatus').html(`
                        <div class="alert alert-danger">
                            <p>Payment initiation failed: ${data.message}</p>
                            <button class="btn btn-secondary" onclick="location.reload()">Try Again</button>
                        </div>
                    `);
                }
            })
            .catch(error => {
                $('#paymentStatus').html(`
                    <div class="alert alert-danger">
                        <p>An error occurred: ${error}</p>
                        <button class="btn btn-secondary" onclick="location.reload()">Try Again</button>
                    </div>
                `);
            });
        });
    }

    function checkPaymentStatus(checkoutRequestId) {
        const checkStatus = function() {
            fetch(`/check_payment_status/${checkoutRequestId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.status === 'completed') {
                            $('#paymentStatus').html(`
                                <div class="alert alert-success">
                                    <p>Payment successful! Receipt: ${data.receipt_number}</p>
                                    <p>Your subscription has been activated.</p>
                                    <button class="btn btn-success" onclick="location.reload()">Continue</button>
                                </div>
                            `);
                        } else if (data.status === 'failed') {
                            $('#paymentStatus').html(`
                                <div class="alert alert-danger">
                                    <p>Payment failed. Please try again.</p>
                                    <button class="btn btn-secondary" onclick="location.reload()">Try Again</button>
                                </div>
                            `);
                        } else {
                            // Still pending, check again in 3 seconds
                            setTimeout(checkStatus, 3000);
                        }
                    } else {
                        $('#paymentStatus').html(`
                            <div class="alert alert-danger">
                                <p>Error checking payment status: ${data.message}</p>
                                <button class="btn btn-secondary" onclick="location.reload()">Try Again</button>
                            </div>
                        `);
                    }
                })
                .catch(error => {
                    $('#paymentStatus').html(`
                        <div class="alert alert-danger">
                            <p>An error occurred: ${error}</p>
                            <button class="btn btn-secondary" onclick="location.reload()">Try Again</button>
                        </div>
                    `);
                });
        };

        // Start checking status
        checkStatus();
    }
});