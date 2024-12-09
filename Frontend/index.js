// Fetch weather data and generate line chart
function fetchWeatherData() {
  document.getElementById("weather_chart").innerHTML = "";
  document.getElementById("chartLegend").innerHTML = "";

  const countyName = document.getElementById("countyName").value;
  const infoTypes = Array.from(
    document.querySelectorAll('input[name="typeOfInformation"]:checked')
  ).map((checkbox) => checkbox.value);
  const fromDate = document.getElementById("fromDate").value;
  const toDate = document.getElementById("toDate").value;

  // Validating fromDate is before toDate
  if (new Date(fromDate) > new Date(toDate)) {
    alert("The 'From' date cannot be later than the 'To' date.");
    return;
  }

  const url = `http://127.0.0.1:5000/weather?countyName=${encodeURIComponent(
    countyName
  )}&typeOfInformation=${encodeURIComponent(
    infoTypes.join(",")
  )}&fromDate=${encodeURIComponent(fromDate)}&toDate=${encodeURIComponent(
    toDate
  )}`;

  axios
    .get(url)
    .then((response) => {
      const data = response.data;

      if (data.error) {
        alert(data.error);
        return;
      }

      const chartData = data.data.map((info) => ({
        info_type: info.info_type,
        values: info.values.map((item) => {
          const formattedDate = new Date(item.Date);
          const month = (formattedDate.getMonth() + 1)
            .toString()
            .padStart(2, "0");
          const day = formattedDate.getDate().toString().padStart(2, "0");
          const year = formattedDate.getFullYear();
          const formattedDateStr = `${month}/${day}/${year}`;
          return [formattedDateStr, item.value];
        }),
      }));

      anychart.onDocumentReady(function () {
        const chart = anychart.line();
        chart.title(
          `Weather Data for ${countyName} from ${fromDate} to ${toDate}`
        );

        // Setting up legend styles
        const legendContainer = document.getElementById("chartLegend");
        legendContainer.innerHTML = "";
        legendContainer.style.display = "flex";
        legendContainer.style.flexWrap = "wrap";
        legendContainer.style.justifyContent = "center";
        legendContainer.style.backgroundColor = "#004070";
        legendContainer.style.padding = "10px";
        legendContainer.style.borderRadius = "5px";
        legendContainer.style.marginTop = "10px";

        const legendColors = [
          "#FF0000",
          "#00FF00",
          "#0000FF",
          "#FFFF00",
          "#FF00FF",
          "#00FFFF",
          "#FFA500",
          "#800080",
        ];

        chartData.forEach((series, index) => {
          const data = anychart.data.set(series.values);
          const lineSeries = chart.line(data);
          lineSeries.name(series.info_type);

          const legendColor = legendColors[index % legendColors.length];
          lineSeries.stroke(legendColor);

          // Creating legend item
          const legendItem = document.createElement("div");
          legendItem.style.color = legendColor;
          legendItem.style.marginRight = "15px";
          legendItem.style.display = "flex";
          legendItem.style.alignItems = "center";

          legendItem.innerHTML = `<span style="color:${legendColor}; margin-right: 5px;">●</span> ${series.info_type}`;
          legendContainer.appendChild(legendItem);
        });

        // Customize axes
        chart.xAxis().title("Date");
        chart.xAxis().labels().rotation(-40);
        chart.yAxis().title("Values");
        chart.container("weather_chart");
        chart.draw();
      });
    })
    .catch((error) => {
      console.error("Error fetching weather data:", error);
      document.getElementById("result").innerText = "Error fetching data";
    });
}
