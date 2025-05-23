import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import FavoritesPage from '../Favorites';
import axios from 'axios';
import { MemoryRouter } from 'react-router-dom';
import { vi, expect, it, describe } from 'vitest';

vi.mock('axios');
vi.mock('../components/GameBox', () => ({
  default: ({ game, onUnfavorite }) => (
    <div data-testid="gamebox">
      {game.name}
      <button onClick={onUnfavorite}>Unfavorite</button>
    </div>
  ),
}));

vi.mock('../AppHeader', () => ({
  default: () => <header data-testid="app-header">AppHeader</header>,
}));

vi.mock('../Pagination', () => ({
  default: ({ currentPage, totalPages, onPageChange }) => (
    <div data-testid="pagination">
      <button onClick={() => onPageChange(currentPage - 1)} disabled={currentPage === 1}>
        Prev
      </button>
      <span>
        {currentPage} / {totalPages}
      </span>
      <button onClick={() => onPageChange(currentPage + 1)} disabled={currentPage === totalPages}>
        Next
      </button>
    </div>
  ),
}));


vi.mock('../utils/Api', () => ({
  getCsrfToken: vi.fn().mockResolvedValue('fake-csrf-token'),
}));

describe('FavoritesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading spinner initially and then favorites', async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        results: [
          { appid: 1, name: 'Game 1', header_image: 'img1.jpg' },
          { appid: 2, name: 'Game 2', header_image: 'img2.jpg' },
        ],
        count: 20,
      },
    });

    render(
      <MemoryRouter>
        <FavoritesPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Game 1')).toBeInTheDocument();
      expect(screen.getByText('Game 2')).toBeInTheDocument();
    });

    expect(screen.getByTestId('pagination')).toHaveTextContent('1 / 2');
  });

  it('shows error message when API fails', async () => {
    axios.get.mockRejectedValueOnce(new Error('API Error'));

    render(
      <MemoryRouter>
        <FavoritesPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Failed to fetch favorites')).toBeInTheDocument();
    });
  });

  it('changes pages when pagination buttons are clicked', async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        results: [{ appid: 1, name: 'Game 1', header_image: 'img1.jpg' }],
        count: 20,
      },
    });

    axios.get.mockResolvedValueOnce({
      data: {
        results: [{ appid: 2, name: 'Game 2', header_image: 'img2.jpg' }],
        count: 20,
      },
    });

    render(
      <MemoryRouter>
        <FavoritesPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Game 1')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Next'));

    await waitFor(() => {
      expect(screen.getByText('Game 2')).toBeInTheDocument();
    });
  });
});
