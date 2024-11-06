const provincesAndCities = {
    "Metro Manila": ["Manila", "Quezon City", "Pasig", "Makati", "Taguig"],
    "Cebu": ["Cebu City", "Lapu-Lapu City", "Mandaue City", "Talisay City", "Toledo City"],
    "Davao del Sur": ["Davao City", "Digos City", "Bansalan"],
    "Benguet": ["Baguio City", "La Trinidad", "Itogon", "Tuba"],
    "Iloilo": ["Iloilo City", "Passi City", "Santa Barbara", "Oton"],
    "Misamis Oriental": ["Cagayan de Oro", "Gingoog City", "El Salvador", "Opol"],
    "South Cotabato": ["General Santos", "Koronadal", "Polomolok", "Tupi"],
    "Zamboanga del Sur": ["Zamboanga City", "Pagadian City", "Molave"],
    "Pampanga": ["Magalang", "Arayat", "Mexico", "Santa Ana", "Bacolor", "Santa Rita", "Guagua", "Lubao", "Sasmuan", "San Fernando",
        "Candaba", "San Luis", "Santo Tomas", "San Simon", "Minalin",
        "Apalit", "Macabebe", "Masantol"
    ],
    "Batangas": ["Batangas City", "Lipa City", "Tanauan"],
    "Laguna": ["Calamba", "Santa Rosa", "San Pablo", "Biñan"],
    "Cavite": ["Tagaytay", "Dasmariñas", "Bacoor", "Cavite City"],
    "Negros Occidental": ["Bacolod City", "Talisay City", "Silay City"],
    "Palawan": ["Puerto Princesa", "Coron", "El Nido"],
    "Bohol": ["Tagbilaran City", "Panglao", "Ubay"]
    // Add more provinces and cities as needed
};

const cityPostalCodes = {
    "Manila": "1000",
    "Quezon City": "1100",
    "Pasig": "1600",
    "Makati": "1200",
    "Taguig": "1630",
    "Cebu City": "6000",
    "Lapu-Lapu City": "6015",
    "Mandaue City": "6014",
    "Talisay City": "6045",
    "Toledo City": "6038",
    "Davao City": "8000",
    "Digos City": "8001",
    "Bansalan": "8012",
    "Baguio City": "2600",
    "La Trinidad": "2601",
    "Itogon": "2602",
    "Tuba": "2603",
    "Iloilo City": "5000",
    "Passi City": "5037",
    "Santa Barbara": "5005",
    "Oton": "5021",
    "Cagayan de Oro": "9000",
    "Gingoog City": "9022",
    "El Salvador": "9012",
    "Opol": "9013",
    "General Santos": "9500",
    "Koronadal": "9506",
    "Polomolok": "9507",
    "Tupi": "9511",
    "Zamboanga City": "7000",
    "Pagadian City": "7016",
    "Molave": "7015",
    "Magalang": "2011",
    "Arayat": "2023",
    "Mexico": "2022",
    "Santa Ana": "2027",
    "Bacolor": "2002",
    "Santa Rita": "2003",
    "Guagua": "2006",
    "Lubao": "2004",
    "Sasmuan": "2017",
    "San Fernando": "2000",
    "Candaba": "2012",
    "San Luis": "2014",
    "Santo Tomas": "2015",
    "San Simon": "2026",
    "Minalin": "2028",
    "Apalit": "2013",
    "Macabebe": "2029",
    "Masantol": "2030",
    // Add more cities and their postal codes as needed
};
// Function to populate city dropdown based on selected province
function updateCity() {
    const provinceSelect = document.getElementById("tar_province");
    const citySelect = document.getElementById("tar_city");
    const selectedProvince = provinceSelect.value;

    // Clear existing city options
    citySelect.innerHTML = '<option value="" disabled selected>Select a city</option>';

    // Get cities for the selected province
    const cities = provincesAndCities[selectedProvince];

    // Populate cities in the city dropdown
    if (cities) {
        cities.forEach(city => {
            const option = document.createElement("option");
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
    }
}

// Function to populate postal code dropdown based on selected city
function updatePostalCode() {
    const citySelect = document.getElementById("tar_city");
    const postalCodeSelect = document.getElementById("tar_postalcode");
    const selectedCity = citySelect.value;

    // Clear existing postal code options
    postalCodeSelect.innerHTML = '<option value="" disabled selected>Select a postal code</option>';

    // Get the postal code for the selected city
    const postalCode = cityPostalCodes[selectedCity];

    if (postalCode) {
        // Create a single option for the postal code
        const option = document.createElement("option");
        option.value = postalCode;
        option.textContent = postalCode;
        postalCodeSelect.appendChild(option);
    }
}