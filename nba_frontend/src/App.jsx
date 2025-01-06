import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import ClusterAnalysis from './pages/ClusterAnalysis';
import SeasonalDistribution from './pages/SeasonalDistribution';
import ConferenceComparison from './pages/ConferenceComparison';

// Import base styles
import './styles/base.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    }
  }
});

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="app">
          <Navbar />
          <main className="container">
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