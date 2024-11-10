// routes/cityName.js
const express = require('express');
const router = express.Router();
const { MongoClient } = require('mongodb');
const ngeohash = require('ngeohash');
const { haversine } = require('../utils/harvesine');

const connString = process.env.MONGO_DB_CONN_STRING;
let mongoClient = null;

router.get('/', async (req, res) => {
    const language = req.query.language;
    const longitude = parseFloat(req.query.longitude);
    const latitude = parseFloat(req.query.latitude);

    if (isNaN(longitude) || isNaN(latitude)) {
        return res.status(400).json({ error: 'Missing or invalid coordinates' });
    }

    try {
        if (!mongoClient) {
            mongoClient = new MongoClient(connString, { useNewUrlParser: true, useUnifiedTopology: true });
            await mongoClient.connect();
        }

        const geohash = ngeohash.encode(latitude, longitude).substring(0, 4);
        const neighbors = ngeohash.neighbors(geohash).map(hash => hash.substring(0, 4));
        const geohashesToCheck = [geohash, ...neighbors];

        const database = mongoClient.db('city-names-db');
        const collection = database.collection('cities_database');
        const query = { geohash: { $in: geohashesToCheck.map(hash => new RegExp(`^${hash}`)) } };
        const results = await collection.find(query).toArray();

        let filteredResults = results.filter(city => {
            const distance = haversine(latitude, longitude, city.latitude, city.longitude);
            return distance <= (city.estimated_radius / 1000);
        });

        if (filteredResults.length === 0) {
            filteredResults = results.filter(city => {
                const distance = haversine(latitude, longitude, city.latitude, city.longitude);
                return distance <= 12 && city.population > 300000;
            });
        }

        if (filteredResults.length === 0) {
            filteredResults = results.filter(city => {
                const distance = haversine(latitude, longitude, city.latitude, city.longitude);
                return distance <= 8 && city.population > 100000;
            });
        }

        if (filteredResults.length === 0) {
            filteredResults = results.filter(city => {
                const distance = haversine(latitude, longitude, city.latitude, city.longitude);
                return distance <= 4 && city.population > 100000;
            });
        }

        if (filteredResults.length === 0) {
            filteredResults = results.filter(city => {
                const distance = haversine(latitude, longitude, city.latitude, city.longitude);
                return distance <= 2;
            });
        }

        if (filteredResults.length === 0) {
            return res.status(404).json({ error: 'No cities found within the specified radius' });
        }

        const nearestCity = filteredResults.reduce((nearest, city) => {
            const distance = haversine(latitude, longitude, city.latitude, city.longitude);
            return distance < nearest.distance ? { city, distance } : nearest;
        }, { city: null, distance: Infinity }).city;

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
                return res.status(404).json({ error: `No data found for language: ${language}` });
            }
        } else {
            result = {
                geonameId: nearestCity.geoname_id_city,
                countryCode: nearestCity.country_code,
                name: nearestCity.name
            };
        }

        return res.json(result);
    } catch (error) {
        console.error('Error processing request', error);
        return res.status(500).json({ error: 'Error processing request' });
    }
});

module.exports = router;