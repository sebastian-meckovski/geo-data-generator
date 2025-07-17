// app/api/city-info-by-ascii/route.ts

import { NextRequest, NextResponse } from 'next/server';
import clientPromise from '@/utils/mongodb';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const countryCode = searchParams.get('country_code')?.toUpperCase() || null;
  const adminArea = searchParams.get('admin_area'); // Optional
  const cityName = searchParams.get('city_name'); // Optional
  const language = searchParams.get('language'); // Optional

  if (!countryCode) {
    return NextResponse.json(
      { error: 'Missing country_code parameter' },
      { status: 400 }
    );
  }

  try {
    const client = await clientPromise;
    const database = client.db('city-names-db');
    const collection = database.collection('cities-collection');

    const query: any = { 
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
      return NextResponse.json(
        { error: 'City not found' },
        { status: 404 }
      );
    }

    // Format the output based on the language parameter
    const formattedResult = {
      geonameId: parseInt(result.geoname_id_city["$numberInt"] || result.geoname_id_city),
      countryCode: result.country_code,
      name: language ? { [language]: result.name[language] } : result.name,
      latitude: parseFloat(result.latitude["$numberDouble"] || result.latitude),
      longitude: parseFloat(result.longitude["$numberDouble"] || result.longitude)
    };

    return NextResponse.json(formattedResult);

  } catch (error) {
    console.error('Error processing request', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
