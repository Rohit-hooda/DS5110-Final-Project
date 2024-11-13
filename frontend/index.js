function fetchWeatherData() {
    const countyName = document.getElementById("countyName").value;
    const typeOfInformation = document.getElementById("typeOfInformation").value;

    const url = `http://127.0.0.1:5000/weather?countyName=${encodeURIComponent(countyName)}&typeOfInformation=${encodeURIComponent(typeOfInformation)}`;

    axios.get(url)
        .then(response => {
            const data = response.data;

            // Handle error if data is not returned properly
            if (data.error) {
                alert(data.error);
                return;
            }

            // Clear the existing chart content in 'weather_chart' container
            document.getElementById("weather_chart").innerHTML = '';

            // Process data for AnyChart
            const chartData = data.data.map(item => [item.date, item.value]);
            const chartTitle = `${data.info_type} over Time for ${data.county_name}`;

            // Create and render the new chart
            anychart.onDocumentReady(function() {
                const chart = anychart.line();
                chart.data(chartData);
                chart.title(chartTitle);
                chart.xAxis().title('Date');
                chart.yAxis().title(data.info_type);
                chart.container('weather_chart');
                chart.draw();
            });

            // Clear previous results and show the chart container
            document.getElementById("result").innerHTML = '';
            document.getElementById("graph-container").style.display = 'block';
        })
        .catch(error => {
            console.error("Error fetching weather data:", error);
            document.getElementById("result").innerText = "Error fetching data";
        });
}
