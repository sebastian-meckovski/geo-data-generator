const express = require('express');
const router = express.Router();
const { MongoClient } = require('mongodb');

const connString = process.env.MONGO_DB_CONN_STRING;
let mongoClient = null;

router.get('/', async (req, res) => {
    const countryCode = req.query.country_code;
    const language = req.query.language;

    if (!countryCode) {
        return res.status(400).json({ error: 'Missing country_code parameter' });
    }

    try {
        if (!mongoClient) {
            mongoClient = new MongoClient(connString, { useNewUrlParser: true, useUnifiedTopology: true });
            await mongoClient.connect();
        }

        const database = mongoClient.db('city-names-db');
        const collection = database.collection('cities_database');

        const query = { country_code: countryCode, feature_code: 'PPLC' };
        const capital = await collection.findOne(query);

        if (!capital) {
            return res.status(404).json({ error: `No capital found for country code ${countryCode}` });
        }

        let result;
        if (language) {
            if (capital.name[language]) {
                result = {
                    geonameId: capital.geoname_id_city,
                    countryCode: capital.country_code,
                    name: {
                        [language]: capital.name[language]
                    },
                    latitude: capital.latitude,
                    longitude: capital.longitude
                };
            } else {
                return res.status(404).json({ error: `No data found for language: ${language}` });
            }
        } else {
            result = {
                geonameId: capital.geoname_id_city,
                countryCode: capital.country_code,
                name: capital.name,
                latitude: capital.latitude,
                longitude: capital.longitude
            };
        }

        return res.json(result);

    } catch (error) {
        console.error('Error processing request', error);
        return res.status(500).json({ error: 'Error processing request' });
    }
});

module.exports = router;