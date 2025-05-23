import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import FavoritesPage from '../Favorites';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';
import React from 'react';

vi.mock('axios', () => ({
  default: {
    get: vi.fn((url) => {
      if (url.includes('/user/favorites/')) {
        return Promise.resolve({ data: { results: [
          { appid: 1, name: 'Fav Game', header_image: 'img.jpg' }
        ], count: 1 } });
      }
      return Promise.resolve({ data: {} });
    }),
    delete: vi.fn(() => Promise.resolve()),
  },
}));

vi.mock('../GameBox', () => ({
  default: ({ game, onUnfavorite }) => (
    <div data-testid="gamebox">
      <span>{game.name}</span>
      <button onClick={onUnfavorite}>Unfavorite</button>
    </div>
  )
}));

vi.mock('../AppHeader', () => ({
  default: () => <div data-testid="appheader">Header</div>
}));

vi.mock('../Pagination', () => ({
  default: ({ currentPage, totalPages, onPageChange }) => (
    <div data-testid="pagination">
      <button onClick={() => onPageChange(1)}>Page 1</button>
    </div>
  )
}));

vi.mock('../../utils/Api', () => ({
  getCsrfToken: vi.fn(() => Promise.resolve('dummy-csrf-token')),
  handleSteamLogout: vi.fn(),
}));

describe('FavoritesPage', () => {
  it('renders favorite games', async () => {
    render(
      <MemoryRouter>
        <FavoritesPage />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Fav Game')).toBeInTheDocument();
    });
  });

  it('handles unfavorite', async () => {
    render(
      <MemoryRouter>
        <FavoritesPage />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Fav Game')).toBeInTheDocument();
    });
    const unfavBtn = screen.getByText('Unfavorite');
    fireEvent.click(unfavBtn);
    await waitFor(() => {
      expect(screen.getByText('Fav Game')).toBeInTheDocument();
    });
  });

  it('shows error on fetch failure', async () => {
    const axios = (await import('axios')).default;
    axios.get.mockImplementationOnce(() => Promise.reject(new Error('fail')));
    render(
      <MemoryRouter>
        <FavoritesPage />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText(/failed to fetch favorites/i)).toBeInTheDocument();
    });
  });
});
