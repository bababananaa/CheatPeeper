// This is the first JavaScript file that runs. It finds the empty
// <div id="root"> in index.html and tells React to draw our <App /> inside it.
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css' // global styles (Tailwind + our colors and font)

createRoot(document.getElementById('root')!).render(
  // StrictMode only runs in development. It double-checks our components
  // and warns us in the browser console about common mistakes.
  <StrictMode>
    <App />
  </StrictMode>,
)
