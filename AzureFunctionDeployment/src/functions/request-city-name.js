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

app.http('request-city-name', {
    methods: ['GET'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        context.log(`Http function processed request for url "${request.url}"`);
        const language = request.query.get('language');
        const longitude = parseFloat(request.query.get('longitude'));
        const latitude = parseFloat(request.query.get('latitude'));

        if (!language || isNaN(longitude) || isNaN(latitude)) {
            return { body: 'Missing or invalid parameters', status: 400 };
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
            const databaseName = `cities_${language}`;
            const database = mongoClient.db(databaseName);
            const collection = database.collection('your-collection-name');
            const query = { geohash: { $regex: `^${geohash}` } };
            const results = await collection.find(query).toArray();

            return { body: results };
        } catch (error) {
            context.log.error('Error processing request', error);
            return { body: 'Error processing request' };
        }
    }
});
