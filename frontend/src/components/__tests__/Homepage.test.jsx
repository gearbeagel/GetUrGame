import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import Homepage from '../Homepage.jsx';
import { vi, describe, it, expect } from 'vitest';

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { redirect_url: 'http://test-redirect' } }))
  },
  get: vi.fn(() => Promise.resolve({ data: { redirect_url: 'http://test-redirect' } }))
}));

describe('Homepage', () => {
  it('renders login button when not authenticated', () => {
    render(<Homepage isAuthenticated={false} username={null} />);
    expect(screen.getByRole('button', { name: /login with steam/i })).toBeInTheDocument();
  });

  it('redirects to Steam on login button click', async () => {
    let href = '';
    delete window.location;
    window.location = {};
    Object.defineProperty(window.location, 'href', {
      set: (val) => { href = val; },
      get: () => href,
      configurable: true,
    });
    render(<Homepage isAuthenticated={false} username={null} />);
    const button = screen.getByRole('button', { name: /login with steam/i });
    fireEvent.click(button);
    await new Promise(r => setTimeout(r, 10));
    expect(href).toBe('http://test-redirect');
  });
});
