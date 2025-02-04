import React, { Component } from 'react';
import '../styles/common.css';

class ErrorBoundary extends Component {
 constructor(props) {
   super(props);
   this.state = { hasError: false, error: null };
 }

 static getDerivedStateFromError(error) {
   return { hasError: true, error };
 }

 componentDidCatch(error, errorInfo) {
   console.error('Error caught by boundary:', error, errorInfo);
 }

 render() {
   if (this.state.hasError) {
     return (
       <div className="error">
         <h2>Something went wrong</h2>
         <p>{this.state.error?.message}</p>
         <button 
           className="button"
           onClick={() => window.location.reload()}
         >
           Reload Page
         </button>
       </div>
     );
   }

   return this.props.children;
 }
}

export { Navbar, Loading, ErrorBoundary };