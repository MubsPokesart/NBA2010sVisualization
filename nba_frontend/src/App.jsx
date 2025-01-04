import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import ClusterAnalysis from './pages/ClusterAnalysis';
import SeasonalDistribution from './pages/SeasonalDistribution';
import ConferenceComparison from './pages/ConferenceComparison';
import { QueryClient, QueryClientProvider } from 'react-query';

const queryClient = new QueryClient();

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
    </QueryClientProvider>
  );
};

export default App;
