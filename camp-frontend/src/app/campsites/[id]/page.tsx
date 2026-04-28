import Link from 'next/link';
import { notFound } from 'next/navigation';
import { CampsiteDetailSection, FacilityItem } from '@/components/CampsiteDetailSection';
import fs from 'fs/promises';
import path from 'path';
import Script from 'next/script';

async function getCampsite(id: string) {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/api/campsites`, {
      cache: 'no-store' // Ensure we get fresh data if it changes
    });
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const campsites = await res.json();
    const campsite = campsites.find((camp: { id: string }) => camp.id === id);
    return campsite || null;
  } catch (error) {
    console.error("Failed to fetch campsite:", error);
    return null;
  }
}

export async function generateStaticParams() {
  const dataDirectory = path.join(process.cwd(), 'data');
  const filePath = path.join(dataDirectory, 'campsites.json');
  const fileContent = await fs.readFile(filePath, 'utf-8');
  const campsites = JSON.parse(fileContent);

  return campsites.map((campsite: { id: string }) => ({
    id: campsite.id,
  }));
}

export default async function CampsiteDetailPage({ params }: { params: { id: string } }) {
  const { id } = await params;
  const campsite = await getCampsite(id);

  if (!campsite) {
    notFound();
  }

  return (
    <>
      <Script
        // src='https://d3rzchwrt70me2.cloudfront.net/'
        src="/widget.iife.js"
        strategy='afterInteractive'
      />
      <div className="bg-gray-50 min-h-screen">
        <div className="container mx-auto p-4 md:p-8">
          <Link href="/campsites" className="text-blue-600 hover:underline mb-6 inline-block flex items-center gap-2">
            &larr; Back to Campsites
          </Link>

          <div className="bg-white rounded-xl shadow-lg p-6 md:p-10 mb-8">
            <h1 className="text-4xl md:text-6xl font-extrabold mb-4 text-gray-900 leading-tight">{campsite.name}</h1>
            <div className="flex items-center text-xl text-gray-500 mb-2">
              <span className="font-medium text-gray-700">{campsite.location.city}, {campsite.location.country}</span>
              <span className="mx-2">•</span>
              <span>{campsite.location.region}</span>
            </div>
            <div className="text-sm text-gray-400">
              Coords: {campsite.location.coordinates.latitude}, {campsite.location.coordinates.longitude}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-6">
              <CampsiteDetailSection title="Facilities">
                <FacilityItem label="Toilets Count" value={campsite.facilities.toilets.count} />
                <FacilityItem label="Hot Showers" value={campsite.facilities.toilets.hot_showers} isBoolean />
                <FacilityItem label="Wheelchair Accessible Toilets" value={campsite.facilities.toilets.wheelchair_accessible} isBoolean />
                <FacilityItem label="Drinking Water" value={campsite.facilities.water.drinking_water} isBoolean />
                <FacilityItem label="Electricity" value={campsite.facilities.electricity.available} isBoolean />
                <FacilityItem label="EV Charging" value={campsite.facilities.ev_charging.available} isBoolean />
                {campsite.facilities.ev_charging.available && (
                  <>
                    <FacilityItem label="Charging Points" value={campsite.facilities.ev_charging.charging_points} />
                    <FacilityItem label="Charging Speed" value={campsite.facilities.ev_charging.charging_speed} />
                    <FacilityItem label="Connectors" value={campsite.facilities.ev_charging.connector_types} isList />
                  </>
                )}
                {!campsite.facilities.ev_charging.available && campsite.facilities.ev_charging.note && (
                  <div className="col-span-2 text-sm text-amber-600 italic mt-2">{campsite.facilities.ev_charging.note}</div>
                )}
              </CampsiteDetailSection>

              <CampsiteDetailSection title="Rules & Vehicles">
                <FacilityItem label="Quiet Hours" value={`${campsite.rules.quiet_hours.start} - ${campsite.rules.quiet_hours.end}`} />
                <FacilityItem label="Pets Allowed" value={campsite.rules.pets.allowed} isBoolean />
                {campsite.rules.pets.restrictions && (
                  <div className="col-span-2 text-sm text-gray-600 mt-1 mb-2">Note: {campsite.rules.pets.restrictions}</div>
                )}
                <FacilityItem label="Max Height" value={campsite.rules.vehicles.max_height} />
                <FacilityItem label="Max Length" value={campsite.rules.vehicles.max_length} />
                {campsite.rules.vehicles.note && (
                  <div className="col-span-2 text-sm text-amber-600 italic mt-2">{campsite.rules.vehicles.note}</div>
                )}
              </CampsiteDetailSection>

              {campsite.accessibility && (
                <CampsiteDetailSection title="Accessibility">
                  <FacilityItem label="Accessible Pitches" value={campsite.accessibility.wheelchair_accessible_pitches} />
                  <FacilityItem label="Accessible Toilets" value={campsite.accessibility.accessible_toilets} isBoolean />
                  <FacilityItem label="Accessible Showers" value={campsite.accessibility.accessible_showers} isBoolean />
                  <FacilityItem label="Ramps" value={campsite.accessibility.ramps} />
                  {campsite.accessibility.terrain_difficulty && (
                    <FacilityItem label="Terrain" value={campsite.accessibility.terrain_difficulty} />
                  )}
                </CampsiteDetailSection>
              )}
            </div>

            <div className="space-y-6">
              <CampsiteDetailSection title="Amenities & Fun">
                <FacilityItem label="Restaurants" value={campsite.amenities.restaurants} />
                <FacilityItem label="Shops" value={campsite.amenities.shops} />
                <FacilityItem label="Swimming Pool" value={campsite.amenities.swimming_pool} isBoolean />
                <FacilityItem label="Playground" value={campsite.amenities.playground} isBoolean />
                <FacilityItem label="Wi-Fi" value={campsite.amenities.wifi} isBoolean />
                {campsite.amenities.wifi_speed && (
                  <FacilityItem label="Wi-Fi Speed" value={campsite.amenities.wifi_speed} />
                )}
              </CampsiteDetailSection>

              {campsite.reviews && campsite.reviews.length > 0 && (
                <div className="mb-6 p-4 border border-gray-200 rounded-lg shadow-sm bg-white">
                  <h2 className="text-2xl font-semibold mb-4 text-gray-700">Reviews ({campsite.reviews.length})</h2>
                  <div className="space-y-4">
                    {campsite.reviews.map((review: { rating: number; verified?: boolean; comment: string; date?: string }, index: number) => (
                      <div key={index} className="border-b border-gray-100 last:border-0 pb-4 last:pb-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded text-sm font-bold">
                            {review.rating.toFixed(1)} / 5.0
                          </span>
                          {review.verified && (
                            <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded uppercase font-semibold">
                              Verified
                            </span>
                          )}
                        </div>
                        <p className="text-gray-700 italic leading-relaxed">&quot;{review.comment}&quot;</p>
                        {review.date && (
                          <p className="text-xs text-gray-400 mt-2">{review.date}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {campsite.extra_costs && (
                <CampsiteDetailSection title="Extra Costs">
                  {Object.entries(campsite.extra_costs).map(([key, value]) => (
                    <FacilityItem key={key} label={key.replace(/_/g, ' ')} value={value as string} />
                  ))}
                </CampsiteDetailSection>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
