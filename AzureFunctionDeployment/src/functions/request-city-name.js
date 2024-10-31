const { app } = require('@azure/functions');
const { DefaultAzureCredential } = require('@azure/identity');
const { SecretClient } = require('@azure/keyvault-secrets');

const keyVaultName = "MongoDB-credentials";
const keyVaultUrl = `https://${keyVaultName}.vault.azure.net`;
const credential = new DefaultAzureCredential();
const client = new SecretClient(keyVaultUrl, credential);

app.http('request-city-name', {
    methods: ['GET'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        context.log(`Http function processed request for url "${request.url}"`);
        const name = request.query.get('name') || await request.text() || 'world';

        try {
            const secretName = "geo-names-mongo-connection-string";
            const secret = await client.getSecret(secretName);
            const connectionString = secret.value;

            return { body: `Retrieved connection string: ${connectionString}` };
        } catch (error) {
            context.log.error('Error retrieving secret from Key Vault', error);
            return { body: 'Error retrieving secret from Key Vault' };
        }
    }
});
