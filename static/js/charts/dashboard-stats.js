/**
 * Dashboard statistikalari uchun JavaSript funksiyalar
 * Chart.js yordamida grafiklarni yaratish
 */

// Sotuvlar grafiklarini yaratish
function createSalesChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: data.datasets[0].label,
                data: data.datasets[0].data,
                backgroundColor: data.datasets[0].backgroundColor,
                borderColor: data.datasets[0].borderColor,
                borderWidth: 1,
                tension: 0.4
            }]
        },
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
                            return context.dataset.label + ': ' + context.raw.toLocaleString() + " so'm";
                        }
                    }
                }
            }
        }
    });
}

// Pie chart yaratish (kategoriyalar)
function createPieChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.datasets[0].data,
                backgroundColor: data.datasets[0].backgroundColor,
                borderColor: data.datasets[0].borderColor,
                borderWidth: 1
            }]
        },
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
                            return context.label + ': ' + value.toLocaleString() + " so'm (" + percentage + "%)";
                        }
                    }
                }
            }
        }
    });
}

// Bar chart yaratish (oylik sotuvlar)
function createBarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: data.datasets[0].label,
                data: data.datasets[0].data,
                backgroundColor: data.datasets[0].backgroundColor,
                borderColor: data.datasets[0].borderColor,
                borderWidth: 1
            }]
        },
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
                            return context.dataset.label + ': ' + context.raw.toLocaleString() + " so'm";
                        }
                    }
                }
            }
        }
    });
}

// Grafiklarga sanadan sanagacha filtrlashni qo'shish
function addDateRangeFilter(formId, chartInstances) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const startDate = form.querySelector('[name="start_date"]').value;
        const endDate = form.querySelector('[name="end_date"]').value;

        // Barcha grafiklarni yangilash
        updateCharts(chartInstances, startDate, endDate);
    });
}

// Barcha grafiklarni yangilash
function updateCharts(chartInstances, startDate, endDate) {
    // Har bir grafik uchun ma'lumot so'rash va yangilash
    for (const [chartId, chartInstance] of Object.entries(chartInstances)) {
        // Ma'lumot so'rash uchun URL yaratish
        const url = new URL(chartInstance.dataUrl, window.location.origin);

        // Filtrlar qo'shish
        if (startDate) url.searchParams.append('start_date', startDate);
        if (endDate) url.searchParams.append('end_date', endDate);

        // Ma'lumotlarni olish
        fetch(url)
            .then(response => response.json())
            .then(data => {
                // Grafik turini tekshirish va mos ravishda yangilash
                if (chartInstance.chart.config.type === 'line' || chartInstance.chart.config.type === 'bar') {
                    chartInstance.chart.data.labels = data.labels;
                    chartInstance.chart.data.datasets[0].data = data.datasets[0].data;
                } else if (chartInstance.chart.config.type === 'pie') {
                    chartInstance.chart.data.labels = data.labels;
                    chartInstance.chart.data.datasets[0].data = data.data.datasets[0].data;
                }

                // Grafikni yangilash
                chartInstance.chart.update();
            })
            .catch(error => console.error(`Error updating chart: ${error}`));
    }
}