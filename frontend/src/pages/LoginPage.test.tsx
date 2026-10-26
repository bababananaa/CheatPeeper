// Tests for the login page. Run them with: npm test
//
// These tests never talk to the real backend. Instead, we replace the
// browser's fetch() with a fake version that returns whatever response
// each test needs (success, wrong password, etc.).
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import LoginPage from './LoginPage.tsx'

// Swaps fetch() for a fake that always answers with this status code and body.
// Returns the fake so a test can check what was sent to it.
function mockFetch(status: number, body: object = {}) {
  const fakeFetch = vi.fn().mockResolvedValue(new Response(JSON.stringify(body), { status }))
  vi.stubGlobal('fetch', fakeFetch)
  return fakeFetch
}

// Fills in the form and clicks "Sign In" the same way a real user would.
async function signIn(email: string, password: string) {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText('Email'), email)
  await user.type(screen.getByLabelText('Password'), password)
  await user.click(screen.getByRole('button', { name: 'Sign In' }))
}

describe('LoginPage', () => {
  it('sends the email and password to the backend and shows a success message', async () => {
    const fakeFetch = mockFetch(200, { access_token: 'fake-token', token_type: 'bearer' })
    render(<LoginPage />)

    await signIn('Albert@ufl.edu', 'password123')

    // findBy... waits for the message to appear, since login happens asynchronously.
    expect(await screen.findByRole('status')).toHaveTextContent('Signed in as albert@ufl.edu')

    // Check that the request matches what the backend's /auth/login expects:
    // a POST with form data, where the email goes in the "username" field.
    const [url, options] = fakeFetch.mock.calls[0]
    expect(url).toMatch(/\/auth\/login$/)
    expect(options.method).toBe('POST')
    expect(options.body.toString()).toBe('username=albert%40ufl.edu&password=password123')
  })

  it('rejects emails that are not @ufl.edu without contacting the backend', async () => {
    const fakeFetch = mockFetch(200)
    render(<LoginPage />)

    await signIn('albert@gmail.com', 'password123')

    expect(screen.getByRole('alert')).toHaveTextContent('Please use your @ufl.edu email.')
    expect(fakeFetch).not.toHaveBeenCalled()
  })

  it('shows an error when the email or password is wrong (401)', async () => {
    mockFetch(401, { detail: 'Incorrect username or password' })
    render(<LoginPage />)

    await signIn('albert@ufl.edu', 'wrong-password')

    expect(await screen.findByRole('alert')).toHaveTextContent('Incorrect email or password.')
  })

  it('asks the user to verify their email when the account is not verified (403)', async () => {
    mockFetch(403, { detail: 'Email not verified' })
    render(<LoginPage />)

    await signIn('albert@ufl.edu', 'password123')

    expect(await screen.findByRole('alert')).toHaveTextContent('Please verify your email before signing in.')
  })

  it('shows a message when the server cannot be reached', async () => {
    // A rejected fetch is what happens when the backend isn't running.
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    render(<LoginPage />)

    await signIn('albert@ufl.edu', 'password123')

    expect(await screen.findByRole('alert')).toHaveTextContent("Can't reach the server.")
  })

  it('shows and hides the password', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)
    const passwordBox = screen.getByLabelText('Password')

    // Hidden (dots) by default
    expect(passwordBox).toHaveAttribute('type', 'password')

    await user.click(screen.getByRole('button', { name: 'Show password' }))
    expect(passwordBox).toHaveAttribute('type', 'text')

    await user.click(screen.getByRole('button', { name: 'Hide password' }))
    expect(passwordBox).toHaveAttribute('type', 'password')
  })
})
