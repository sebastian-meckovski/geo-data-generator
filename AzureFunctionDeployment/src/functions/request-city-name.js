const { app } = require('@azure/functions');
const { DefaultAzureCredential } = require('@azure/identity');
const { SecretClient } = require('@azure/keyvault-secrets');
const { MongoClient } = require('mongodb');
const ngeohash = require('ngeohash');

const keyVaultName = "MongoDB-credentials";
const keyVaultUrl = `https://${keyVaultName}.vault.azure.net`;
const credential = new DefaultAzureCredential();
const client = new SecretClient(keyVaultUrl, credential);

let cachedSecret = null;
let mongoClient = null;

// Haversine formula to calculate the distance between two points on the Earth
function haversine(lat1, lon1, lat2, lon2) {
    const toRadians = (degrees) => degrees * (Math.PI / 180);
    const R = 6371; // Radius of the Earth in kilometers
    const dLat = toRadians(lat2 - lat1);
    const dLon = toRadians(lon1 - lon2);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in kilometers
}

app.http('city-name', {
    methods: ['GET'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        context.log(`Http function processed request for url "${request.url}"`);
        const language = request.query.get('language');
        const longitude = parseFloat(request.query.get('longitude'));
        const latitude = parseFloat(request.query.get('latitude'));

        if (isNaN(longitude) || isNaN(latitude)) {
            return { body: JSON.stringify({ error: 'Missing or invalid coordinates' }), status: 400, headers: { 'Content-Type': 'application/json' } };
        }

        try {
            if (!cachedSecret) {
                const secretName = "geo-names-mongo-connection-string";
                const secret = await client.getSecret(secretName);
                cachedSecret = secret.value;
            }

            if (!mongoClient) {
                mongoClient = new MongoClient(cachedSecret, { useNewUrlParser: true, useUnifiedTopology: true });
                await mongoClient.connect();
            }

            const geohash = ngeohash.encode(latitude, longitude).substring(0, 4);
            const neighbors = ngeohash.neighbors(geohash).map(hash => hash.substring(0, 4));
            const geohashesToCheck = [geohash, ...neighbors];

            const database = mongoClient.db('city-names-db');
            const collection = database.collection('cities-collection');
            const query = { geohash: { $in: geohashesToCheck.map(hash => new RegExp(`^${hash}`)) } };
            const results = await collection.find(query).toArray();

            // Filter results based on estimated radius and search radius
            let filteredResults = results.filter(city => {
                const distance = haversine(latitude, longitude, city.latitude, city.longitude);
                return distance <= (city.estimated_radius / 1000); // Convert radius to kilometers
            });

            // If no results found, check within a 12 km radius and population > 300,000
            if (filteredResults.length === 0) {
                filteredResults = results.filter(city => {
                    const distance = haversine(latitude, longitude, city.latitude, city.longitude);
                    return distance <= 12 && city.population > 300000; 
                });
            }

            // If still no results, check within an 8 km radius and population > 100,000
            if (filteredResults.length === 0) {
                filteredResults = results.filter(city => {
                    const distance = haversine(latitude, longitude, city.latitude, city.longitude);
                    return distance <= 8 && city.population > 100000; 
                });
            }

            // If still no results, check within an 8 km radius and population > 100,000
            if (filteredResults.length === 0) {
                filteredResults = results.filter(city => {
                    const distance = haversine(latitude, longitude, city.latitude, city.longitude);
                    return distance <= 4 && city.population > 100000; 
                });
            }
            // If still no results, check within an 2 km radius
            if (filteredResults.length === 0) {
                filteredResults = results.filter(city => {
                    const distance = haversine(latitude, longitude, city.latitude, city.longitude);
                    return distance <= 2; 
                });
            }

            if (filteredResults.length === 0) {
                return { body: JSON.stringify({ error: 'No cities found within the specified radius' }), status: 404, headers: { 'Content-Type': 'application/json' } };
            }

            // Find the nearest city center
            const nearestCity = filteredResults.reduce((nearest, city) => {
                const distance = haversine(latitude, longitude, city.latitude, city.longitude);
                return distance < nearest.distance ? { city, distance } : nearest;
            }, { city: null, distance: Infinity }).city;

            // Prepare the result based on the language parameter
            let result;
            if (language) {
                if (nearestCity.name[language]) {
                    result = {
                        geonameId: nearestCity.geoname_id_city,
                        countryCode: nearestCity.country_code,
                        name: {
                            [language]: nearestCity.name[language]
                        }
                    };
                } else {
                    return { body: JSON.stringify({ error: `No data found for language: ${language}` }), status: 404, headers: { 'Content-Type': 'application/json' } };
                }
            } else {
                result = {
                    geonameId: nearestCity.geoname_id_city,
                    countryCode: nearestCity.country_code,
                    name: nearestCity.name
                };
            }

            return { body: JSON.stringify(result), headers: { 'Content-Type': 'application/json' } };
        } catch (error) {
            context.log.error('Error processing request', error);
            return { body: JSON.stringify({ error: 'Error processing request' }), status: 500, headers: { 'Content-Type': 'application/json' } };
        }
    }
});
