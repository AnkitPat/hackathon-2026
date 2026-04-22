import Link from 'next/link';

interface CampsiteCardProps {
  id: string;
  name: string;
  location: {
    city: string;
    country: string;
  };
}

export const CampsiteCard = ({ id, name, location }: CampsiteCardProps) => {
  return (
    <Link 
      href={`/campsites/${id}`}
      className="block p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
    >
      <h2 className="text-xl font-bold text-gray-900 mb-2">{name}</h2>
      <p className="text-gray-600">
        {location.city}, {location.country}
      </p>
    </Link>
  );
};
