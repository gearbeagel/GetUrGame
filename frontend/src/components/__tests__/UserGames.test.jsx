import { describe, it, vi, beforeEach, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import GamesPage from '../UserGames.jsx';
import axios from 'axios';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('../components/GameBox', () => ({
  default: ({ game }) => <div data-testid="gamebox">{game.name}</div>
}));
vi.mock('../AppHeader', () => ({
  default: () => <header data-testid="app-header">AppHeader</header>
}));
vi.mock('../Pagination', () => ({
  default: ({ currentPage, totalPages }) => (
    <div data-testid="pagination">
      Page {currentPage} of {totalPages}
    </div>
  )
}));

vi.mock('axios');

describe('GamesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading spinner initially and fetches data', async () => {
    axios.get.mockResolvedValue({
      data: {
        results: [{ id: 1, appid: 123, name: 'Test Game', cover_url: 'test.jpg' }],
        count: 10
      }
    });

    render(
      <MemoryRouter>
        <GamesPage />
      </MemoryRouter>
    );

    // Expect loading spinner (you can adjust selector accordingly)
    expect(screen.getByTestId('app-header')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Test Game')).toBeInTheDocument();
    });

    expect(screen.getByTestId('pagination')).toBeInTheDocument();
  });

  it('displays error if API fails', async () => {
    axios.get.mockRejectedValue(new Error('API Error'));

    render(
      <MemoryRouter>
        <GamesPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Failed to fetch games')).toBeInTheDocument();
    });
  });

  it('renders multiple game boxes', async () => {
    const mockGames = Array.from({ length: 5 }, (_, i) => ({
      id: i + 1,
      appid: 100 + i,
      name: `Game ${i + 1}`,
      cover_url: `cover${i + 1}.jpg`
    }));

    axios.get.mockResolvedValue({
      data: {
        results: mockGames,
        count: 50
      }
    });

    render(
      <MemoryRouter>
        <GamesPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getAllByText(/game /i)).toHaveLength(5);
    });
  });
});
