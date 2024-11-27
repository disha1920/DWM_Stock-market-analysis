// Wait for the DOM to fully load before running any script
document.addEventListener('DOMContentLoaded', function () {

    // Smooth scroll to sections when a link is clicked
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Form validation logic
    const form = document.querySelector('form');
    form.addEventListener('submit', function (event) {
        const tickerInput = document.querySelector('#ticker');
        const monthSelect = document.querySelector('#month');

        // Basic validation for stock ticker input
        if (tickerInput.value.trim() === "") {
            alert("Please enter a valid stock ticker.");
            tickerInput.focus();
            event.preventDefault();  // Prevent form submission
            return false;
        }

        // Basic validation for month selection
        if (!monthSelect.value) {
            alert("Please select a valid month.");
            monthSelect.focus();
            event.preventDefault();  // Prevent form submission
            return false;
        }

        // Show loading spinner when form is submitted
        const submitButton = document.querySelector('button[type="submit"]');
        submitButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Processing...';
        submitButton.disabled = true;
    });

    // Loading indicators for graphs
    const graphContainers = document.querySelectorAll('.graph-container');
    graphContainers.forEach(container => {
        // Create a loading spinner inside each graph container
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Loading...';
        container.appendChild(spinner);
    });

    // Simulate graph loading (for demo purposes)
    setTimeout(() => {
        graphContainers.forEach(container => {
            const spinner = container.querySelector('.loading-spinner');
            if (spinner) {
                spinner.remove();  // Remove spinner when graph is ready
            }
        });
    }, 2000);  // Simulating 2 seconds load time for graphs

});

// Function to display loading spinner for predictions
function showPredictionLoader() {
    const summaryContainer = document.querySelector('.prediction-summary');
    summaryContainer.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Generating prediction...';
}

