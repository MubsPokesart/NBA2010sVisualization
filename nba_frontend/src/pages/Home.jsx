import React from 'react';
import '../styles/home.css';

const Home = () => {
  return (
    <div className="home">
      <h1 className="home-title">NBA Performance Analysis 2010-2019</h1>
      <p className="home-description">
        This application visualizes and examines the performance disparity 
        between Eastern and Western Conference teams in the National Basketball 
        Association (NBA) from 2009-10 to 2018-19.
      </p>
      <p className="home-credit">
        Credit to wyattwalsh/nbadb on Kaggle for the data collection
      </p>
    </div>
  );
};

export default Home;