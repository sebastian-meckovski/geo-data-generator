This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/route.ts`. The page auto-updates as you edit the file.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

## API Routes

This directory contains example API routes for the headless API app.

For more details, see [route.js file convention](https://nextjs.org/docs/app/api-reference/file-conventions/route).

### Available Endpoints

#### 1. City Info by Coordinates
`GET /api/city-info-by-coordinates`

Finds the nearest city to given GPS coordinates.

**Query Parameters:**
- `latitude` (required): Latitude coordinate
- `longitude` (required): Longitude coordinate  
- `language` (optional): Language code for localized names

**Example:**
```
GET /api/city-info-by-coordinates?latitude=52.2297&longitude=21.0122&language=en
```

#### 2. City Info by ASCII Name
`GET /api/city-info-by-ascii`

Finds city information by country code and optional city/admin area names.

**Query Parameters:**
- `country_code` (required): ISO country code (e.g., "US", "PL")
- `city_name` (optional): ASCII city name
- `admin_area` (optional): Administrative area name
- `language` (optional): Language code for localized names

**Example:**
```
GET /api/city-info-by-ascii?country_code=PL&city_name=warsaw&language=en
```

#### 3. Search Cities
`GET /api/search`

Search for cities using keywords with MongoDB Atlas Search.

**Query Parameters:**
- `language` (required): Language code for search and results
- `keywords` (required): Space-separated search keywords

**Example:**
```
GET /api/search?language=en&keywords=new york
```

### Environment Variables

Create a `.env.local` file with:
```
MONGO_DB_CONN_STRING=your_mongodb_connection_string
```
