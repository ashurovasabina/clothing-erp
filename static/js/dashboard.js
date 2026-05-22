document.addEventListener('DOMContentLoaded', function() {
    console.log("Dashboard script loaded");

    // Check if we're on the dashboard page by looking for chart canvases
    const salesChartCanvas = document.getElementById('salesChart');
    const categoryChartCanvas = document.getElementById('categoryChart');

    if (!salesChartCanvas || !categoryChartCanvas) {
        console.log("Not on dashboard page or chart elements not found");
        return;
    }

    // Function to create sales chart
    function createSalesChart() {
        const ctx = salesChartCanvas.getContext('2d');

        // Make AJAX request for chart data
        fetch('/en/api/sales-chart/')
            .then(response => response.json())
            .then(data => {
                new Chart(ctx, {
                    type: 'line',
                    data: data,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function(value) {
                                        return value.toLocaleString() + " so'm";
                                    }
                                }
                            }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return context.dataset.label + ': ' +
                                            context.raw.toLocaleString() + " so'm";
                                    }
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => console.error("Error loading sales chart:", error));
    }

    // Function to create category chart
    function createCategoryChart() {
        const ctx = categoryChartCanvas.getContext('2d');

        // Make AJAX request for chart data
        fetch('/en/api/category-distribution/?type=sales')
            .then(response => response.json())
            .then(data => {
                new Chart(ctx, {
                    type: 'pie',
                    data: data.data,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const value = context.raw;
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return context.label + ': ' +
                                            value.toLocaleString() + " so'm (" + percentage + "%)";
                                    }
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => console.error("Error loading category chart:", error));
    }

    // Create charts
    createSalesChart();
    createCategoryChart();
});