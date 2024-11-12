const express = require('express');
const cityNameRoutes = require('./routes/cityName');
const countryCapitalRoutes = require('./routes/countryCapital');
const citySearch = require('./routes/citySearch');



const app = express();
const port = 5050;

// ... (MongoDB connection code can be here or in a separate db.js file)

app.use('/city-name', cityNameRoutes);

app.use('/country-capital', countryCapitalRoutes); // Mount the new route

app.use('/citySearch', citySearch)

// You can add other routes here in the future, e.g.,
// app.use('/other-api', otherApiRoutes);

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});