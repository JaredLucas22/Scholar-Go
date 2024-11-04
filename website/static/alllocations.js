const cityData = {
    Luzon: {
        'Metro Manila': [
            'Quezon City',
            'Makati',
            'Manila',
            'Pasig',
            'Taguig',
            'Parañaque',
            'Caloocan',
            'Las Piñas',
            'Mandaluyong',
            'Malabon',
            'Navotas',
            'Valenzuela',
            'San Juan',
            'Pateros',
            'Marikina',
        ],
        'Bulacan': [
            'Malolos',
            'San Jose del Monte',
            'Meycauayan',
            'Santa Maria',
            'Balagtas',
            'Guiguinto',
            'Bocaue',
            'Pulong Buhangin',
            'Obando',
            'Bulakan',
        ],
        'Cavite': [
            'Kawit',
            'Imus',
            'Dasmariñas',
            'Tagaytay',
            'Gen. Trias',
            'Tanza',
            'Bacoor',
            'Silang',
            'Naic',
            'Rosario',
        ],
        'Rizal': [
            'Antipolo',
            'Rodriguez',
            'Binangonan',
            'Taytay',
            'Montalban',
            'San Mateo',
            'Cainta',
            'Angono',
        ],
        'Laguna': [
            'Santa Rosa',
            'Biñan',
            'Calamba',
            'San Pablo',
            'Luisiana',
            'Bae',
            'Alaminos',
            'Cavinti',
        ],
        'Batangas': [
            'Batangas City',
            'Lipa City',
            'Tanauan',
            'Nasugbu',
            'San Jose',
            'Lemery',
            'Taal',
        ],
        'Pampanga': [
            'San Fernando',
            'Angeles City',
            'Mabalacat',
            'Bacolor',
            'Guagua',
            'Porac',
            'Mexico',
            'Apalit',
            'Macabebe',
            'Masantol',
        ],
        'Nueva Ecija': [
            'Cabanatuan',
            'Gapan',
            'San Jose City',
            'Palayan City',
            'San Antonio',
        ],
        'Tarlac': [
            'Tarlac City',
            'Capas',
            'La Paz',
            'Concepcion',
            'Paniqui',
        ],
        'Aurora': [
            'Baler',
            'Casiguran',
            'Dipaculao',
            'Dilasag',
            'Maria Aurora',
        ],
        'Zambales': [
            'Olongapo City',
            'Subic',
            'San Antonio',
            'Iba',
            'Castillejos',
        ],
        'Quirino': [
            'Cabarroguis',
            'Diffun',
            'Maddela',
            'Nagtipunan',
            'Saguday',
        ],
        'Isabela': [
            'Ilagan',
            'Santiago City',
            'Cauayan City',
            'San Manuel',
            'Angadanan',
        ],
        'La Union': [
            'San Fernando',
            'La Union',
            'Bacnotan',
            'Agoo',
            'Bauang',
        ],
        'Pangasinan': [
            'Lingayen',
            'Dagupan City',
            'San Carlos City',
            'Umingan',
            'Binalonan',
        ],
        // Add more provinces and their cities here
    },
    Visayas: {
        'Cebu': [
            'Cebu City',
            'Mandaue',
            'Lapu-Lapu',
            'Toledo',
            'Talisay',
            'Carcar',
            'Danao',
            'Naga',
            'Bantayan',
            'Malabuyoc',
        ],
        'Iloilo': [
            'Iloilo City',
            'Passi City',
            'San Miguel',
            'Lambunao',
            'Pavia',
            'Leganes',
            'Bingawan',
            'Cabatuan',
            'Janiuay',
        ],
        'Negros Occidental': [
            'Bacolod City',
            'Silay City',
            'San Carlos',
            'Talisay City',
            'Victorias',
            'Bago City',
            'La Carlota',
        ],
        'Leyte': [
            'Tacloban City',
            'Ormoc',
            'Baybay',
            'Burauen',
            'Palo',
            'Tolosa',
            'Tanauan',
        ],
        'Samar': [
            'Catbalogan',
            'Calbayog',
            'Samar',
            'Basey',
            'Gandara',
        ],
        'Bohol': [
            'Tagbilaran City',
            'Dumaguete',
            'Balilihan',
            'Baclayon',
            'Anda',
        ],
        'Aklan': [
            'Kalibo',
            'Boracay',
            'Altavas',
            'Malinao',
            'New Washington',
        ],
        'Antique': [
            'San Jose de Buenavista',
            'Sibalom',
            'Hamtic',
            'Tibiao',
            'Anini-y',
        ],
        'Capiz': [
            'Roxas City',
            'Panay',
            'Mambusao',
            'Pilar',
            'Dumalag',
        ],
        'Negros Oriental': [
            'Dumaguete City',
            'Bayawan City',
            'Tanjay City',
            'Canlaon City',
            'Guihulngan City',
        ],
        // Add more provinces and their cities here
    },
    Mindanao: {
        'Davao': [
            'Davao City',
            'Digos City',
            'Panabo City',
            'Tagum City',
            'Samal City',
            'Bansalan',
            'Baguio District',
        ],
        'Zamboanga': [
            'Zamboanga City',
            'Dipolog',
            'Dapitan',
            'Pagadian',
            'Sibuco',
            'Iligan',
            'Sierra Bullones',
        ],
        'Socsksargen': [
            'General Santos',
            'Koronadal',
            'Tantangan',
            'Surallah',
            'Polomolok',
            'Banga',
            'Alabel',
        ],
        'Northern Mindanao': [
            'Cagayan de Oro',
            'Iligan City',
            'Malaybalay',
            'Gingoog City',
            'Villanueva',
        ],
        'Caraga': [
            'Butuan City',
            'Agusan del Norte',
            'Agusan del Sur',
            'Surigao del Norte',
            'Surigao del Sur',
        ],
        'ARMM': [
            'Cotabato City',
            'Marawi',
            'Lanao del Sur',
            'Sulu',
            'Basilan',
        ],
        'Davao Oriental': [
            'Mati City',
            'Baganga',
            'Banaybanay',
            'Caraga',
            'Governor Generoso',
        ],
        'Sarangani': [
            'Alabel',
            'Glan',
            'Maasim',
            'Malapatan',
            'Sarangani',
        ],
        // Add more provinces and their cities here
    }
};

const postalCodeData = {
    'Quezon City': ['1100', '1101', '1102', '1103', '1104', '1105'],
    'Makati': ['1200', '1201', '1202', '1203', '1204'],
    'Cebu City': ['6000', '6001', '6002', '6003', '6004'],
    'Davao City': ['8000', '8001', '8002', '8003', '8004'],
    'Malolos': ['3000', '3001', '3002'],
    'San Jose del Monte': ['3023', '3024'],
    'Bacoor': ['4102', '4103', '4104'],
    'Cagayan de Oro': ['9000', '9001', '9002'],
    'Iloilo City': ['5000', '5001', '5002'],
    'Tacloban City': ['6500', '6501'],
    'Zamboanga City': ['7000', '7001', '7002'],
    'Tagaytay': ['4120', '4121'],
    'Antipolo': ['1870', '1871'],
    'San Fernando': ['2000', '2001'],
    'Bacolod City': ['6100', '6101'],
    'Calbayog': ['6710', '6711'],
    'Surallah': ['9505', '9506'],
    'Iligan City': ['9200', '9201'],
    'Digos City': ['8000', '8001'],
    'Tagum City': ['8100', '8101'],
    'Angeles City': ['2009', '2010'],
    'Apalit': ['2016'],
    'Macabebe': ['2011'],
    'Masantol': ['2015'],
    'Las Piñas': ['1750', '1751'],
    'Talisay City': ['6045', '6046'],
    'Mandaue': ['6014', '6015'],
    'San Carlos City': ['6127', '6128'],
    // Continue with more cities and their postal codes
};


function fetchCities() {
    const provinceSelect = document.getElementById('tar_province');
    const citySelect = document.getElementById('tar_city');
    const postalCodeSelect = document.getElementById('tar_postalcode');

    // Clear the cities and postal codes select
    citySelect.innerHTML = '<option value="">Select a city</option>';
    postalCodeSelect.innerHTML = '<option value="">Select a postal code</option>';

    const selectedProvince = provinceSelect.value;
    if (selectedProvince) {
        const cities = cityData[selectedProvince];
        for (const city in cities) {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        }
    }
}

function fetchPostalCodes() {
    const citySelect = document.getElementById('tar_city');
    const postalCodeSelect = document.getElementById('tar_postalcode');

    // Clear the postal codes select
    postalCodeSelect.innerHTML = '<option value="">Select a postal code</option>';

    const selectedCity = citySelect.value;
    if (selectedCity) {
        const postalCodes = postalCodeData[selectedCity];
        postalCodes.forEach(code => {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = code;
            postalCodeSelect.appendChild(option);
        });
    }
}

// Dynamic fetching example
async function fetchCitiesFromAPI() {
    const provinceSelect = document.getElementById('tar_province');
    const citySelect = document.getElementById('tar_city');
    const postalCodeSelect = document.getElementById('tar_postalcode');

    citySelect.innerHTML = '<option value="">Select a city</option>';
    postalCodeSelect.innerHTML = '<option value="">Select a postal code</option>';

    const selectedProvince = provinceSelect.value;
    if (selectedProvince) {
        try {
            const response = await fetch(`/api/cities?province=${selectedProvince}`);
            const cities = await response.json();
            cities.forEach(city => {
                const option = document.createElement('option');
                option.value = city;
                option.textContent = city;
                citySelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching cities:', error);
        }
    }
}

async function fetchPostalCodesFromAPI() {
    const citySelect = document.getElementById('tar_city');
    const postalCodeSelect = document.getElementById('tar_postalcode');

    postalCodeSelect.innerHTML = '<option value="">Select a postal code</option>';

    const selectedCity = citySelect.value;
    if (selectedCity) {
        try {
            const response = await fetch(`/api/postalcodes?city=${selectedCity}`);
            const postalCodes = await response.json();
            postalCodes.forEach(code => {
                const option = document.createElement('option');
                option.value = code;
                option.textContent = code;
                postalCodeSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching postal codes:', error);
        }
    }
}
