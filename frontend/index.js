function fetchWeatherData() {
    const countyName = document.getElementById("countyName").value;
    const typeOfInformation = document.getElementById("typeOfInformation").value;

    const url = `http://127.0.0.1:5000/weather?countyName=${encodeURIComponent(countyName)}&typeOfInformation=${encodeURIComponent(typeOfInformation)}`;
    
    axios.get(url)
        .then(response => {
            document.getElementById("result").innerText = JSON.stringify(response.data, null, 2);
        })
        .catch(error => {
            console.error("Error fetching weather data:", error);
            document.getElementById("result").innerText = "Error fetching data";
        });
}
