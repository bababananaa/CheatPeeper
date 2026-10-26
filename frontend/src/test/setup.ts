// Runs before every test file (set up in vite.config.ts).

// Adds extra checks for web pages to expect(), like toBeInTheDocument()
// and toHaveTextContent().
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

// After each test, reset everything so tests can't affect each other:
afterEach(() => {
  cleanup() // remove whatever the test drew on the fake page
  vi.unstubAllGlobals() // put back the real fetch() if a test replaced it
})
