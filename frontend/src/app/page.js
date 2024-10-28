"use client";
import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://127.0.0.1:3001/recommend/', {
        params: { query }
      });
      setResults(response.data.result || []); 
      console.log(results)
    } catch (error) {
      console.error('Error fetching search results:', error);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
      <h1 className="text-4xl mb-6">Product Search</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search products..."
        className="p-2 border border-gray-400 rounded w-1/2 mb-4 text-black" 
      />
      <button
        onClick={handleSearch}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded"
      >
        {loading ? 'Searching...' : 'Search'}
      </button>
      <div className="mt-6 w-1/2">
        {results.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {results.map((product) => (
              <div
                key={product._id}
                className="bg-gray-800 p-4 rounded shadow-md"
              >

                <h2 className="text-xl font-bold">{product["Product Title"]}</h2> 
                <p className="text-sm">{product["Product Description"]}</p> 
                <p className="font-semibold">Price: {product.Price}</p>
                <p className="text-sm">Brand: {product.Brand}</p>
                <p className="text-sm">Stock: {product["Stock Availibility"]}</p> 
              </div>
            ))}
          </div>
        ) : (
          <p>No results found</p>
        )}
      </div>
    </div>
  );
}
