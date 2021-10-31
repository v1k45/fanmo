/* Project specific Javascript goes here. */

// Add a request interceptor
axios.interceptors.request.use(function (config) {
    config.headers["X-CSRFToken"] = Cookies.get('csrftoken');;
    return config;
});

function subscribe(username, amount) {
    axios.post("/api/subscriptions/", {
        username,
        amount
    }).then(function (response) {
        const paymentOptions = response.data.payment_payload;
        paymentOptions.handler = function (rzpResponse) {
            axios.post("/api/payments/", {
                processor: "razorpay",
                type: "subscription",
                payload: rzpResponse
            }).then(paymentReponse => {
                alert("Payment processing successful!");
            })
        }
        var rzp1 = new Razorpay(paymentOptions);
        rzp1.open()
    });
}
