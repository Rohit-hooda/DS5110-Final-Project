// Function to fetch weather data and generate line chart
function fetchWeatherData() {
  // Reset the chart and legend before making a new request
  document.getElementById("weather_chart").innerHTML = "";
  document.getElementById("chartLegend").innerHTML = "";

  const countyName = document.getElementById("countyName").value;
  const infoTypes = Array.from(
    document.querySelectorAll('input[name="typeOfInformation"]:checked')
  ).map((checkbox) => checkbox.value);
  const fromDate = document.getElementById("fromDate").value;
  const toDate = document.getElementById("toDate").value;

  // Validate dates
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
          const formattedDate = new Date(item.Date).toLocaleDateString(
            "en-GB",
            {
              weekday: "short",
              day: "2-digit",
              month: "short",
              year: "numeric",
            }
          );
          return [formattedDate, item.value];
        }),
      }));

      anychart.onDocumentReady(function () {
        const chart = anychart.line();
        chart.title(
          `Weather Data for ${countyName} from ${fromDate} to ${toDate}`
        );

        // Set up legend styles
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

          // Create legend item
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
        chart.xAxis().labels().rotation(-45);
        chart.yAxis().title("Values");

        // Draw chart in container
        chart.container("weather_chart");
        chart.draw();
      });
    })
    .catch((error) => {
      console.error("Error fetching weather data:", error);
      document.getElementById("result").innerText = "Error fetching data";
    });
}


//  Function to fetch current weather data for chloropeth map



// // Function to fetch the heatmap image for a specific feature
// function fetchHeatmap(feature) {
//   // Reset the image before making a new request
//   const heatmapImage = document.getElementById("heatmapImage");
//   heatmapImage.style.display = "none";
//   const heatmapContainer = document.getElementById("heatmapContainer");
//   heatmapContainer.innerHTML = ""; //

//   const countyName = document.getElementById("countyName").value;

//   const url = `http://127.0.0.1:5000/heatmap?feature=${encodeURIComponent(
//     feature
//   )}&countyName=${encodeURIComponent(countyName)}`;

//   axios
//     .get(url, { responseType: "blob" }) // Specify that we expect a binary response (image)
//     .then((response) => {
//       const imageUrl = URL.createObjectURL(response.data); // Create a local URL for the image blob
//       heatmapImage.src = imageUrl; // Set the image source to the new URL
//       heatmapImage.style.display = "block"; // Show the image
//     })
//     .catch((error) => {
//       console.error("Error fetching heatmap data:", error);
//       alert("Error loading heatmap image.");
//     });
// }
