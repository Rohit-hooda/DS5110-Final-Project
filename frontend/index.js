function fetchWeatherData() {
    const countyName = document.getElementById("countyName").value;
    const typeOfInformation = document.getElementById("typeOfInformation").value;

    const url = `http://127.0.0.1:5000/weather?countyName=${encodeURIComponent(countyName)}&typeOfInformation=${encodeURIComponent(typeOfInformation)}`;
    
    axios.get(url, { responseType: 'arraybuffer' })
        .then(response => {
            // Convert the binary data (image) to a Blob
            const blob = new Blob([response.data], { type: 'image/png' });

            // Create a URL for the image Blob
            const imgURL = URL.createObjectURL(blob);

            // Create an image element to display the graph
            const imgElement = document.createElement("img");
            imgElement.src = imgURL;
            imgElement.style.width = '100%';  // Makes the image scale according to the screen width
            imgElement.style.height = 'auto'; // Keeps aspect ratio

            // Clear previous content and append the new image
            document.getElementById("result").innerHTML = '';  // Clear previous results
            document.getElementById("result").appendChild(imgElement);
        })
        .catch(error => {
            console.error("Error fetching weather data:", error);
            document.getElementById("result").innerText = "Error fetching data";
        });
}
