import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import AppHeader from '../AppHeader';
import React from 'react';
import { vi, describe, it, expect } from 'vitest';

describe('AppHeader', () => {
  it('renders all navigation links and logout button', () => {
    render(
      <MemoryRouter>
        <AppHeader showFavorites={true} />
      </MemoryRouter>
    );
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading.textContent.replace(/\s+/g, ' ').toLowerCase()).toContain('get ur game');
    expect(screen.getByRole('link', { name: /your games/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /get recommendations/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /favorites/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });

  it('does not render favorites link if showFavorites is false', () => {
    render(
      <MemoryRouter>
        <AppHeader showFavorites={false} />
      </MemoryRouter>
    );
    expect(screen.queryByRole('link', { name: /favorites/i })).not.toBeInTheDocument();
  });

  it('calls handleSteamLogout when logout button is clicked', () => {
    const logoutMock = vi.fn();
    render(
      <MemoryRouter>
        <AppHeader showFavorites={true} />
      </MemoryRouter>
    );
    const logoutBtn = screen.getByRole('button', { name: /logout/i });
    logoutBtn.onclick = logoutMock;
    fireEvent.click(logoutBtn);
    expect(logoutMock).toHaveBeenCalled();
  });
});
