import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import ClusterAnalysis from './pages/ClusterAnalysis';
import SeasonalDistribution from './pages/SeasonalDistribution';
import ConferenceComparison from './pages/ConferenceComparison';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
      onError: (error) => {
        console.error('Query Error:', error);
      }
    }
  }
});

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-100">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/cluster-analysis" element={<ClusterAnalysis />} />
              <Route path="/seasonal-distribution" element={<SeasonalDistribution />} />
              <Route path="/conference-comparison" element={<ConferenceComparison />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
      <ReactQueryDevtools initialIsOpen={false} /> {/* This will help with debugging */}
    </QueryClientProvider>
  );
};

export default App;