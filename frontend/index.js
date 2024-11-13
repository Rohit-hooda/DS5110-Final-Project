function fetchWeatherData() {
    // Reset the chart and legend before making a new request
    document.getElementById("weather_chart").innerHTML = '';
    document.getElementById('chartLegend').innerHTML = '';

    const countyName = document.getElementById("countyName").value;
    const infoTypes = Array.from(document.querySelectorAll('input[name="typeOfInformation"]:checked')).map(checkbox => checkbox.value);
    const fromDate = document.getElementById("fromDate").value;
    const toDate = document.getElementById("toDate").value;

    if (new Date(fromDate) > new Date(toDate)) {
        alert("The 'From' date cannot be later than the 'To' date.");
        return;
    }

    const url = `http://127.0.0.1:5000/weather?countyName=${encodeURIComponent(countyName)}&typeOfInformation=${encodeURIComponent(infoTypes.join(','))}&fromDate=${encodeURIComponent(fromDate)}&toDate=${encodeURIComponent(toDate)}`;
    
    axios.get(url)
        .then(response => {
            const data = response.data;

            if (data.error) {
                alert(data.error);
                return;
            }

            const chartData = data.data.map(info => ({
                info_type: info.info_type,
                values: info.values.map(item => {
                    const formattedDate = new Date(item.Date).toLocaleString('en-GB', {
                        weekday: 'short',  
                        day: '2-digit',    
                        month: 'short',    
                        year: 'numeric'   
                    });
                    return [formattedDate, item.value];
                })
            }));

            anychart.onDocumentReady(function() {
                const chart = anychart.line();
                chart.title(`Weather Data from ${fromDate} to ${toDate}`);

                const legendContainer = document.getElementById('chartLegend');
                legendContainer.innerHTML = '';
                legendContainer.style.display = 'flex';
                legendContainer.style.flexWrap = 'wrap';  
                legendContainer.style.justifyContent = 'flex-start'; 

                chartData.forEach((series, index) => {
                    const data = anychart.data.set(series.values);
                    const lineSeries = chart.line(data);
                    lineSeries.name(series.info_type);

                    const legendItem = document.createElement('div');
                    legendItem.style.color = lineSeries.color();
                    legendItem.style.marginRight = '15px';
                    legendItem.style.display = 'flex';
                    legendItem.style.alignItems = 'center';

                    legendItem.innerHTML = `<span style="color:${lineSeries.color()}; margin-right: 5px;">●</span> ${series.info_type}`;
                    legendContainer.appendChild(legendItem);
                });

                chart.xAxis().title('Date');
                chart.yAxis().title('Value');
                chart.container('weather_chart');
                chart.draw();
            });
        })
        .catch(error => {
            console.error("Error fetching weather data:", error);
            document.getElementById("result").innerText = "Error fetching data";
        });
}
