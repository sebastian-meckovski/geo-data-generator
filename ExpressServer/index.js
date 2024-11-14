const express = require('express');
const cors = require('cors');
const cityNameByCoordinates = require('./routes/cityInfoByCoordinates');
const cityNameByAscii = require('./routes/cityInfoByAscii');

const app = express();
const port = 5050;

app.use(cors());

app.use('/city-info-by-coordinates', cityNameByCoordinates);
app.use('/city-info-by-ascii', cityNameByAscii);

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});
