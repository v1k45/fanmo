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
        const paymentOptions = response.data.payload;
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


function submitSubscribe(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    subscribe(formData.get('username'), formData.get('amount'))
}


function cancelSubscription(id) {
    axios.post(`/api/subscriptions/${id}/cancel/`).then(function (response) {
        alert("Cancelled subscription!")
    });
}
