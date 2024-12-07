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
    const language = req.query.language; // Language parameter (e.g., 'pl')
    const keywords = req.query.keywords; // Keywords parameter (e.g., 'buda weg')

    if (!language || !keywords) {
        return res.status(400).json({ error: 'Missing language or keywords parameter' });
    }

    try {
        const client = await getMongoClient();
        const database = client.db('city-names-db');
        const collection = database.collection('cities-collection');

        // Split the keywords into an array of individual words
        const keywordArray = keywords.split(' ').map(word => `*${word}*`);

        // Construct the $search query
        const pipeline = [
            {
                $search: {
                    index: "cities-search-index",
                    compound: {
                        must: keywordArray.map(keyword => ({
                            wildcard: {
                                query: keyword,
                                path: [
                                    `name.${language}.country`,
                                    `name.${language}.admin1`,
                                    `name.${language}.city`,
                                    "name.en.country",
                                    "name.en.admin1",
                                    "name.en.city"
                                ],
                                allowAnalyzedField: true
                            }
                        }))
                    }
                }
            },
            {
                $sort: { population: -1 } // Order by population descending
            },
            {
                $limit: 5 // Limit the results to 5
            }
        ];

        console.log(keywordArray)

        // Execute the aggregation pipeline
        const results = await collection.aggregate(pipeline).toArray();
        console.log

        if (results.length === 0) {
            return res.status(404).json({ error: 'No matching records found' });
        }

        // Prepare the response
        const response = results.map(result => {
            const geonameId = result.geoname_id_city;
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
