// index.js
const express = require('express');
const cors = require('cors');
const cityNameByCoordinates = require('./routes/cityNameByCoordinates');
const cityNameByAscii = require('./routes/cityInfoByAscii');
const search = require('./routes/search'); // Import the new route

const app = express();
const port = 5050;

app.use(cors());

app.use('/city-info-by-coordinates', cityNameByCoordinates);
app.use('/city-info-by-ascii', cityNameByAscii);
app.use('/search', search); // Register the new route

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('Server shutting down...');
    process.exit();
});

// TODO: consolidate mongoDb constants pull from env
