const express = require('express');
const router = express.Router();
const { MongoClient } = require('mongodb');

const connString = process.env.MONGO_DB_CONN_STRING;
let mongoClient = null;

// Function to get MongoDB client
async function getMongoClient() {
    if (!mongoClient) {
        mongoClient = new MongoClient(connString);
        await mongoClient.connect();
    }
    return mongoClient;
}

// Ensure MongoDB client is closed on process exit
process.on('SIGINT', async () => {
    if (mongoClient) {
        await mongoClient.close();
        console.log('MongoDB connection closed.');
    }
    process.exit();
});

router.get('/', async (req, res) => {
    const language = req.query.language;
    const keyword = req.query.keyword;

    if (!language || !keyword) {
        return res.status(400).json({ error: 'Missing language or keyword parameter' });
    }

    try {
        const client = await getMongoClient();
        const database = client.db('city-names-db');
        const collection = database.collection('cities_database');

        // Define collation for the query
        const collation = {
            locale: 'en', // Use 'pl' for non-English searches, fallback to 'en' for English
            strength: 1 // Case-insensitive and diacritic-insensitive
        };

        // Build the query for the specified language
        const query = {
            $or: [
                { [`name.${language}.city`]: keyword },
                { [`name.${language}.admin1`]: keyword },
                { [`name.${language}.country`]: keyword }
            ]
        };
        console.log('Trying in original langauge', language)

        // Execute the search query, ordered by population (descending), limited to 5 results
        let results = await collection.find(query)
            .collation(collation)
            .sort({ population: -1 }) // Order by population descending
            .limit(5)
            .toArray();

        // Fallback to English if no results found
        if (results.length === 0) {
            console.log('results are empty. Trying english')
            const fallbackQuery = {
                $or: [
                    { 'name.en.city': { $regex: keyword, $options: 'i' } },
                    { 'name.en.admin1': { $regex: keyword, $options: 'i' } },
                    { 'name.en.country': { $regex: keyword, $options: 'i' } }
                ]
            };

            results = await collection.find(fallbackQuery)
                .collation({ locale: 'en', strength: 1 })
                .sort({ population: -1 })
                .limit(5)
                .toArray();
        }

        // If still no results found, return 404
        if (results.length === 0) {
            return res.status(404).json({ error: 'No matching records found' });
        }

        // Prepare the response
        const response = results.map(result => {
            const geonameId = parseInt(result.geoname_id_city["$numberInt"] || result.geoname_id_city);
            const countryCode = result.country_code;
            const nameData = result.name[language] || result.name['en'];
            return {
                geonameId,
                countryCode,
                name: {
                    [language]: nameData
                }
            };
        });

        return res.json(response);

    } catch (error) {
        console.error('Error processing request:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;
