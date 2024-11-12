const express = require('express');
const router = express.Router();
const { MongoClient } = require('mongodb');

const connString = process.env.MONGO_DB_CONN_STRING;
let mongoClient = null;

router.get('/', async (req, res) => {
  const countryCode = req.query.country_code;
  const adminArea = req.query.admin_area; // Optional
  const cityName = req.query.city_name; // Optional
  const language = req.query.language; // Optional

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

    const query = { 
      'country_code': countryCode 
    };

    // Add city and admin area to the query if provided
    if (cityName) {
      query['name.ascii.city'] = cityName;
    }
    if (adminArea) {
      query['name.ascii.admin1'] = adminArea.toLowerCase().replace(/-/g, ' ');
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
      geonameId: result.geoname_id_city,
      countryCode: result.country_code,
      name: language ? { [language]: result.name[language] } : result.name,
      latitude: result.latitude,
      longitude: result.longitude
    };

    return res.json(formattedResult);

  } catch (error) {
    console.error('Error processing request', error);
    return res.status(500).json({ error: 'Error processing request' });
  }
});

module.exports = router;