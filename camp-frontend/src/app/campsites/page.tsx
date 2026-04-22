import { CampsiteCard } from '@/components/CampsiteCard';

interface Campsite {
  id: string;
  name: string;
  location: {
    city: string;
    country: string;
  };
}

async function getCampsites(): Promise<Campsite[]> {
  // Using absolute URL for Server Component fetch
  const res = await fetch('http://localhost:3000/api/campsites', {
    next: { revalidate: 3600 } // Cache for 1 hour
  });

  if (!res.ok) {
    throw new Error('Failed to fetch campsites');
  }

  return res.json();
}

export default async function CampsitesPage() {
  const campsites = await getCampsites().catch((error) => {
    console.error('Error in CampsitesPage:', error);
    return null;
  });

  if (campsites === null) {
    return (
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">All Campsites</h1>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline"> Failed to load campsites. Please ensure the local server is running on http://localhost:3000.</span>
        </div>
      </main>
    );
  }

  if (campsites.length === 0) {
    return (
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8 text-gray-900">All Campsites</h1>
        <p className="text-gray-600 text-center py-12">No campsites found.</p>
      </main>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8 text-gray-900">All Campsites</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {campsites.map((campsite) => (
          <CampsiteCard
            key={campsite.id}
            id={campsite.id}
            name={campsite.name}
            location={campsite.location}
          />
        ))}
      </div>
    </main>
  );
}
