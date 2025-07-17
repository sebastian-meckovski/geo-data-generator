// app/api/city-info-by-coordinates/route.ts

import { NextRequest, NextResponse } from 'next/server';
import clientPromise from '@/utils/mongodb';
import { haversine } from '@/utils/haversine';
import * as ngeohash from 'ngeohash';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const language = searchParams.get('language');
  const longitude = parseFloat(searchParams.get('longitude') || '');
  const latitude = parseFloat(searchParams.get('latitude') || '');

  if (isNaN(longitude) || isNaN(latitude)) {
    return NextResponse.json(
      { error: 'Missing or invalid coordinates' },
      { status: 400 }
    );
  }

  try {
    const client = await clientPromise;

    const geohash = ngeohash.encode(latitude, longitude).substring(0, 4);
    const neighbors = ngeohash.neighbors(geohash).map((hash: string) => hash.substring(0, 4));
    const geohashesToCheck = [geohash, ...neighbors];

    const database = client.db('city-names-db');
    const collection = database.collection('cities-collection');
    const query = { geohash: { $in: geohashesToCheck.map(hash => new RegExp(`^${hash}`)) } };
    const results = await collection.find(query).toArray();

    // Filtering logic remains unchanged
    let filteredResults = results.filter((city: any) => {
      const distance = haversine(latitude, longitude, city.latitude, city.longitude);
      return distance <= (city.estimated_radius / 1000);
    });

    if (filteredResults.length === 0) {
      filteredResults = results.filter((city: any) => {
        const distance = haversine(latitude, longitude, city.latitude, city.longitude);
        return distance <= 12 && city.population > 300000;
      });
    }

    if (filteredResults.length === 0) {
      filteredResults = results.filter((city: any) => {
        const distance = haversine(latitude, longitude, city.latitude, city.longitude);
        return distance <= 8 && city.population > 100000;
      });
    }

    if (filteredResults.length === 0) {
      filteredResults = results.filter((city: any) => {
        const distance = haversine(latitude, longitude, city.latitude, city.longitude);
        return distance <= 4 && city.population > 100000;
      });
    }

    if (filteredResults.length === 0) {
      filteredResults = results.filter((city: any) => {
        const distance = haversine(latitude, longitude, city.latitude, city.longitude);
        return distance <= 2;
      });
    }

    if (filteredResults.length === 0) {
      return NextResponse.json(
        { error: 'No cities found within the specified radius' },
        { status: 404 }
      );
    }

    const nearestCity = filteredResults.reduce((nearest: any, city: any) => {
      const distance = haversine(latitude, longitude, city.latitude, city.longitude);
      return distance < nearest.distance ? { city, distance } : nearest;
    }, { city: null, distance: Infinity }).city;

    let result: any;
    if (language) {
      if (nearestCity.name[language]) {
        result = {
          geonameId: nearestCity.geoname_id_city,
          countryCode: nearestCity.country_code,
          name: {
            [language]: nearestCity.name[language]
          }
        };
      } else {
        return NextResponse.json(
          { error: `No data found for language: ${language}` },
          { status: 404 }
        );
      }
    } else {
      result = {
        geonameId: nearestCity.geoname_id_city,
        countryCode: nearestCity.country_code,
        name: nearestCity.name
      };
    }

    return NextResponse.json(result);
  } catch (error) {
    console.error('Error processing request', error);
    return NextResponse.json(
      { error: 'Error processing request' },
      { status: 500 }
    );
  }
}
