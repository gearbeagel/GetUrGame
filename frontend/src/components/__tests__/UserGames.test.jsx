import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import GamesPage from '../UserGames';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';

vi.mock('axios', () => ({
  default: {
    get: vi.fn((url) => {
      if (url.includes('/user/games/')) {
        return Promise.resolve({ data: { results: [
          { id: 1, appid: 1, name: 'User Game', cover_url: 'img.jpg' }
        ], count: 1 } });
      }
      return Promise.resolve({ data: {} });
    }),
  },
}));

vi.mock('../GameBox', () => ({
  default: ({ game }) => (
    <div data-testid="gamebox">
      <span>{game.name}</span>
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

describe('GamesPage', () => {
  it('renders user games', async () => {
    render(
      <MemoryRouter>
        <GamesPage />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('User Game')).toBeInTheDocument();
    });
  });

  it('shows error on fetch failure', async () => {
    const axios = (await import('axios')).default;
    axios.get.mockImplementationOnce(() => Promise.reject(new Error('fail')));
    render(
      <MemoryRouter>
        <GamesPage />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText(/failed to fetch games/i)).toBeInTheDocument();
    });
  });

  it('handles pagination', async () => {
    render(
      <MemoryRouter>
        <GamesPage />
      </MemoryRouter>
    );
    const pageBtn = await screen.findByText('Page 1');
    fireEvent.click(pageBtn);
    await waitFor(() => {
      expect(screen.getByText('User Game')).toBeInTheDocument();
    });
  });
});
