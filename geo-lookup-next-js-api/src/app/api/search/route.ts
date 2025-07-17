// app/api/search/route.ts

import { NextRequest, NextResponse } from 'next/server';
import clientPromise from '@/utils/mongodb';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const language = searchParams.get('language'); // Language parameter (e.g., 'pl')
  const keywords = searchParams.get('keywords'); // Keywords parameter (e.g., 'buda weg')

  if (!language || !keywords) {
    return NextResponse.json(
      { error: 'Missing language or keywords parameter' },
      { status: 400 }
    );
  }

  try {
    const client = await clientPromise;
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

    // Execute the aggregation pipeline
    const results = await collection.aggregate(pipeline).toArray();

    if (results.length === 0) {
      return NextResponse.json(
        { error: 'No matching records found' },
        { status: 404 }
      );
    }

    // Prepare the response
    const response = results.map((result: any) => {
      const geonameId = result.geoname_id_city;
      const countryCode = result.country_code;
      const nameData = result.name[language] || result.name['en'];
      const latitude = result.latitude; 
      const longitude = result.longitude;
      return {
        geonameId,
        countryCode,
        name: {
          [language]: nameData
        },
        latitude,
        longitude 
      };
    });

    return NextResponse.json(response);

  } catch (error) {
    console.error('Error processing request:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
