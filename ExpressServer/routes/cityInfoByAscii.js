// routes/cityInfoByAscii.js

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
  const countryCode = req.query.country_code ? req.query.country_code.toUpperCase() : null;
  const adminArea = req.query.admin_area; // Optional
  const cityName = req.query.city_name; // Optional
  const language = req.query.language; // Optional

  if (!countryCode) {
    return res.status(400).json({ error: 'Missing country_code parameter' });
  }

  try {
    const client = await getMongoClient();
    const database = client.db('city-names-db');
    const collection = database.collection('cities-collection');

    const query = { 
      'country_code': countryCode 
    };

    // Add city and admin area to the query if provided
    if (cityName) {
      query['name.ascii.city'] = cityName.toLowerCase();
    }
    if (adminArea) {
      query['name.ascii.admin1'] = adminArea.toLowerCase();
    }

    // If no city is provided, assume it's a request for the capital
    if (!cityName) {
      query.feature_code = 'PPLC'; // Assuming capitals have feature_code 'PPLC'
    }

    const result = await collection.findOne(query);

    if (!result) {
      return res.status(404).json({ error: 'City not found' });
    }

    // Format the output based on the language parameter
    let formattedResult = {
      geonameId: parseInt(result.geoname_id_city["$numberInt"] || result.geoname_id_city),
      countryCode: result.country_code,
      name: language ? { [language]: result.name[language] } : result.name,
      latitude: parseFloat(result.latitude["$numberDouble"] || result.latitude),
      longitude: parseFloat(result.longitude["$numberDouble"] || result.longitude)
    };

    return res.json(formattedResult);

  } catch (error) {
    console.error('Error processing request', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;