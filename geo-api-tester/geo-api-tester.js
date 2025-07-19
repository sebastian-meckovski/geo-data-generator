// Initialize the map
const map = L.map('map').setView([47.39514642720356, 19.0320586928338], 10);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
}).addTo(map);

// Get DOM elements
const languageSelect = document.getElementById('language-select');
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');
const cityNameInput = document.getElementById('city-name-input');
const countryCodeInput = document.getElementById('country-code-input');
const adminAreaInput = document.getElementById('admin-area-input');
const asciiSearchButton = document.getElementById('ascii-search-button');
const searchResults = document.getElementById('search-results');
const searchResultsList = document.getElementById('search-results-list');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const errorMessage = document.getElementById('error-message');
const noDataDiv = document.getElementById('no-data');
const noDataMessage = document.getElementById('no-data-message');
const infoContent = document.getElementById('info-content');
const apiStatus = document.getElementById('api-status');

// Current marker reference
let currentMarker = null;

// Function to show loading state
function showLoading() {
    loadingDiv.classList.remove('hidden');
    errorDiv.classList.add('hidden');
    noDataDiv.classList.add('hidden');
    apiStatus.textContent = 'Loading...';
    apiStatus.className = 'text-blue-500';
}

// Function to hide loading state
function hideLoading() {
    loadingDiv.classList.add('hidden');
}

// Function to show error
function showError(message) {
    errorMessage.textContent = message;
    errorDiv.classList.remove('hidden');
    loadingDiv.classList.add('hidden');
    noDataDiv.classList.add('hidden');
    apiStatus.textContent = 'Error';
    apiStatus.className = 'text-red-500';
}

// Function to show no data message
function showNoData(message = 'No cities found within the specified radius') {
    noDataMessage.textContent = message;
    noDataDiv.classList.remove('hidden');
    errorDiv.classList.add('hidden');
    loadingDiv.classList.add('hidden');
    apiStatus.textContent = 'No Data';
    apiStatus.className = 'text-yellow-600';
}

// Function to hide all messages
function hideAllMessages() {
    errorDiv.classList.add('hidden');
    noDataDiv.classList.add('hidden');
    searchResults.classList.add('hidden');
}

// Function to search for cities by ASCII name
async function searchCityByAscii(cityName, countryCode, adminArea, language) {
    let apiUrl = `https://geo-lookup-api.vercel.app/api/city-info-by-ascii?language=${language}&city_name=${encodeURIComponent(cityName)}&country_code=${countryCode.toUpperCase()}`;
    
    if (adminArea && adminArea.trim()) {
        apiUrl += `&admin_area=${encodeURIComponent(adminArea)}`;
    }
    
    try {
        showLoading();
        hideAllMessages();
        
        const response = await fetch(apiUrl);
        
        if (response.status === 404) {
            hideLoading();
            showNoData('City not found with the specified criteria');
            return null;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        hideLoading();
        
        return data;
    } catch (error) {
        hideLoading();
        console.error('Error searching city by ASCII:', error);
        showError(`Failed to find city: ${error.message}`);
        throw error;
    }
}

// Function to search for cities
async function searchCities(keywords, language) {
    const apiUrl = `https://geo-lookup-api.vercel.app/api/search?language=${language}&keywords=${encodeURIComponent(keywords)}`;
    
    try {
        showLoading();
        hideAllMessages();
        
        const response = await fetch(apiUrl);
        
        if (response.status === 404) {
            hideLoading();
            showNoData('No cities found for your search');
            return [];
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        hideLoading();
        
        return data;
    } catch (error) {
        hideLoading();
        console.error('Error searching cities:', error);
        showError(`Failed to search cities: ${error.message}`);
        throw error;
    }
}

// Function to display search results
function displaySearchResults(results) {
    if (results.length === 0) {
        showNoData('No cities found for your search');
        return;
    }
    
    searchResultsList.innerHTML = '';
    
    results.forEach(city => {
        const language = languageSelect.value;
        const cityName = city.name[language]?.city || 'Unknown';
        const countryName = city.name[language]?.country || 'Unknown';
        const admin1Name = city.name[language]?.admin1 || '';
        
        const resultElement = document.createElement('div');
        resultElement.className = 'p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-colors';
        resultElement.innerHTML = `
            <div class="flex justify-between items-center">
                <div>
                    <div class="font-medium text-gray-900">${cityName}</div>
                    <div class="text-sm text-gray-600">
                        ${admin1Name ? admin1Name + ', ' : ''}${countryName}
                    </div>
                </div>
                <div class="text-xs text-gray-500">
                    ${city.latitude.toFixed(4)}, ${city.longitude.toFixed(4)}
                </div>
            </div>
        `;
        
        // Add click handler to navigate to the city
        resultElement.addEventListener('click', () => {
            navigateToLocation(city.latitude, city.longitude, city);
            searchResults.classList.add('hidden');
            
            // Update API endpoint display for keyword search
            document.querySelector('.text-xs.break-all').textContent = 'search';
        });
        
        searchResultsList.appendChild(resultElement);
    });
    
    searchResults.classList.remove('hidden');
}

// Function to reset info panel to initial state
function resetInfoPanel() {
    infoContent.innerHTML = `
        <div class="text-center py-8">
            <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <p class="text-gray-500 mb-2">No location selected</p>
            <p class="text-sm text-gray-400">Search for cities or click anywhere on the map to get detailed location information</p>
        </div>
        <div class="border-t border-gray-200 pt-4 mt-4">
            <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                    <span class="font-medium">API Endpoint:</span>
                    <span class="text-xs break-all text-gray-500">city-info-by-coordinates</span>
                </div>
                <div class="flex justify-between">
                    <span class="font-medium">Status:</span>
                    <span id="api-status" class="text-gray-500">Ready</span>
                </div>
            </div>
        </div>
    `;
}

// Function to navigate to a specific location
function navigateToLocation(latitude, longitude, cityData = null) {
    // Remove previous marker if exists
    if (currentMarker) {
        map.removeLayer(currentMarker);
    }
    
    // Set map view to the new location
    map.setView([latitude, longitude], 12);
    
    // Add new marker
    currentMarker = L.marker([latitude, longitude]).addTo(map);
    
    if (cityData) {
        // If we have city data from search, use it
        updateInfoPanel(cityData, latitude, longitude);
        
        const language = languageSelect.value;
        const cityName = cityData.name[language]?.city || 'Unknown';
        const countryName = cityData.name[language]?.country || 'Unknown';
        
        currentMarker.bindPopup(`
            <div class="p-2 text-center">
                <div class="font-semibold">${cityName}</div>
                <div class="text-sm text-gray-600">${countryName}</div>
            </div>
        `).openPopup();
    } else {
        // Fetch location data for manually clicked coordinates
        const language = languageSelect.value;
        fetchLocationData(latitude, longitude, language).then(data => {
            if (data) {
                updateInfoPanel(data, latitude, longitude);
                
                // Update API endpoint display for coordinates search
                document.querySelector('.text-xs.break-all').textContent = 'city-info-by-coordinates';
                
                const locationData = data.name[language];
                const city = locationData.city || 'Unknown';
                const country = locationData.country || 'Unknown';
                currentMarker.bindPopup(`
                    <div class="p-2 text-center">
                        <div class="font-semibold">${city}</div>
                        <div class="text-sm text-gray-600">${country}</div>
                    </div>
                `).openPopup();
            } else {
                // No data found - reset info panel to initial state
                resetInfoPanel();
                currentMarker.bindPopup(`
                    <div class="p-2 text-center">
                        <div class="font-semibold text-yellow-600">No Data</div>
                        <div class="text-sm text-gray-600">No cities found</div>
                    </div>
                `).openPopup();
            }
        }).catch(error => {
            console.error('Error fetching location data:', error);
            // Reset info panel on error as well
            resetInfoPanel();
            currentMarker.bindPopup(`
                <div class="p-2 text-center">
                    <div class="font-semibold text-red-600">Error</div>
                    <div class="text-sm text-gray-600">Failed to fetch data</div>
                </div>
            `).openPopup();
        });
    }
}

// Function to update info panel
function updateInfoPanel(data, latitude, longitude) {
    const locationData = data.name[languageSelect.value];
    
    const city = locationData.city || 'Unknown';
    const admin1 = locationData.admin1 || 'N/A';
    const country = locationData.country || 'Unknown';
    const geonameId = data.geonameId || 'N/A';
    const countryCode = data.countryCode || 'N/A';
    
    infoContent.innerHTML = `
        <div class="space-y-4">
            <div class="grid grid-cols-1 gap-3">
                <div class="flex justify-between items-center py-3 border-b border-gray-100">
                    <span class="font-semibold text-gray-700 flex items-center">
                        <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                        </svg>
                        City:
                    </span>
                    <span class="text-gray-900 font-medium">${city}</span>
                </div>
                <div class="flex justify-between items-center py-3 border-b border-gray-100">
                    <span class="font-semibold text-gray-700 flex items-center">
                        <svg class="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m-6 3l6-3"></path>
                        </svg>
                        Administrative Region:
                    </span>
                    <span class="text-gray-900 font-medium">${admin1}</span>
                </div>
                <div class="flex justify-between items-center py-3 border-b border-gray-100">
                    <span class="font-semibold text-gray-700 flex items-center">
                        <svg class="w-4 h-4 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        Country:
                    </span>
                    <span class="text-gray-900 font-medium">${country}</span>
                </div>
            </div>
            
            <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-700 mb-3 flex items-center">
                    <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Technical Details:
                </h4>
                <div class="space-y-2 text-xs text-gray-600">
                    <div class="flex justify-between">
                        <span>Coordinates:</span>
                        <span class="font-mono">${latitude.toFixed(6)}, ${longitude.toFixed(6)}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Geoname ID:</span>
                        <span class="font-mono">${geonameId}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Country Code:</span>
                        <span class="font-mono">${countryCode}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Language:</span>
                        <span class="font-mono">${languageSelect.value.toUpperCase()}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="border-t border-gray-200 pt-4 mt-4">
            <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                    <span class="font-medium">API Endpoint:</span>
                    <span class="text-xs break-all text-gray-500"></span>
                </div>
                <div class="flex justify-between">
                    <span class="font-medium">Status:</span>
                    <span id="api-status" class="text-green-500">Success</span>
                </div>
            </div>
        </div>
    `;
}

// Function to fetch location data
async function fetchLocationData(latitude, longitude, language) {
    // Direct API call - use with CORS-disabled browser for local testing
    const apiUrl = `https://geo-lookup-api.vercel.app/api/city-info-by-coordinates?latitude=${latitude}&longitude=${longitude}&language=${language}`;
    
    try {
        showLoading();
        hideAllMessages();
        
        const response = await fetch(apiUrl);
        
        // Check for 404 specifically
        if (response.status === 404) {
            hideLoading();
            showNoData();
            return null;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        hideLoading();
        
        return data;
    } catch (error) {
        hideLoading();
        console.error('Error fetching location data:', error);
        showError(`Failed to fetch location data: ${error.message}`);
        throw error;
    }
}

// Map click event handler
map.on('click', async function(e) {
    const latitude = e.latlng.lat;
    const longitude = e.latlng.lng;
    
    navigateToLocation(latitude, longitude);
});

// Language change handler - refetch data if marker exists
languageSelect.addEventListener('change', async function() {
    if (currentMarker && currentMarker.getLatLng()) {
        const latlng = currentMarker.getLatLng();
        const latitude = latlng.lat;
        const longitude = latlng.lng;
        const language = languageSelect.value;
        
        try {
            const data = await fetchLocationData(latitude, longitude, language);
            if (data) {
                updateInfoPanel(data, latitude, longitude);
                
                // Update popup content
                const locationData = data.name[language];
                const city = locationData.city || 'Unknown';
                const country = locationData.country || 'Unknown';
                currentMarker.setPopupContent(`
                    <div class="p-2 text-center">
                        <div class="font-semibold">${city}</div>
                        <div class="text-sm text-gray-600">${country}</div>
                    </div>
                `);
                
                // Reopen popup if it was open
                if (currentMarker.isPopupOpen()) {
                    currentMarker.openPopup();
                }
            }
        } catch (error) {
            console.error('Error updating language:', error);
        }
    }
    
    // Hide search results when language changes
    searchResults.classList.add('hidden');
    
    // Clear ASCII search inputs when language changes
    cityNameInput.value = '';
    countryCodeInput.value = '';
    adminAreaInput.value = '';
});

// ASCII search functionality
async function performAsciiSearch() {
    const cityName = cityNameInput.value.trim();
    const countryCode = countryCodeInput.value.trim();
    const adminArea = adminAreaInput.value.trim();
    const language = languageSelect.value;
    
    if (!cityName) {
        showError('Please enter a city name');
        return;
    }
    
    if (!countryCode) {
        showError('Please enter a country code');
        return;
    }
    
    if (countryCode.length !== 2) {
        showError('Country code must be exactly 2 characters (e.g., US, FR, GB)');
        return;
    }
    
    try {
        const result = await searchCityByAscii(cityName, countryCode, adminArea, language);
        if (result) {
            // Navigate directly to the found city
            navigateToLocation(result.latitude, result.longitude, result);
            
            // Update API status to show which endpoint was used
            const endpointUsed = adminArea ? 'city-info-by-ascii (with admin area)' : 'city-info-by-ascii';
            document.querySelector('.text-xs.break-all').textContent = endpointUsed;
        }
    } catch (error) {
        console.error('ASCII search error:', error);
    }
}

// ASCII search button click handler
asciiSearchButton.addEventListener('click', performAsciiSearch);

// ASCII search input enter key handlers
cityNameInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        performAsciiSearch();
    }
});

countryCodeInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        performAsciiSearch();
    }
});

adminAreaInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        performAsciiSearch();
    }
});

// Auto-uppercase country code input
countryCodeInput.addEventListener('input', function(e) {
    e.target.value = e.target.value.toUpperCase();
});

// Search functionality
async function performSearch() {
    const keywords = searchInput.value.trim();
    const language = languageSelect.value;
    
    if (!keywords) {
        showError('Please enter search keywords');
        return;
    }
    
    if (keywords.length < 2) {
        showError('Please enter at least 2 characters');
        return;
    }
    
    try {
        const results = await searchCities(keywords, language);
        displaySearchResults(results);
    } catch (error) {
        console.error('Search error:', error);
    }
}

// Search button click handler
searchButton.addEventListener('click', performSearch);

// Search input enter key handler
searchInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        performSearch();
    }
});

// Clear search results when input is cleared
searchInput.addEventListener('input', function() {
    if (searchInput.value.trim() === '') {
        searchResults.classList.add('hidden');
    }
});

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add initial marker at Budapest
    const initialMarker = L.marker([47.39514642720356, 19.0320586928338]).addTo(map);
    initialMarker.bindPopup(`
        <div class="p-2">
            <h3 class="font-bold text-lg mb-2 text-blue-600">Welcome!</h3>
            <p class="text-sm">This is Budapest, Hungary</p>
            <p class="text-xs text-gray-500 mt-2">Click anywhere on the map to get location information</p>
        </div>
    `);
    
    currentMarker = initialMarker;
});
