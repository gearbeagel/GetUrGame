import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import RecommendationsPage from '../GetRecs';
import { vi, describe, expect, it } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('axios', () => ({
  default: {
    post: vi.fn(() => Promise.resolve({ data: [
      { appid: 1, name: 'Test Game', header_image: 'img.jpg', short_description: 'desc' }
    ]})),
    get: vi.fn(() => Promise.reject({ response: { status: 404 } })),
    delete: vi.fn(() => Promise.resolve()),
  },
}));

vi.mock('../NeonButton', () => ({
  default: ({ children, ...props }) => <button {...props}>{children}</button>
}));

vi.mock('../GameBox', () => ({
  default: ({ game, onFavorite, onUnfavorite, isFavorited }) => (
    <div data-testid="gamebox">
      <span>{game.name}</span>
      <button onClick={onFavorite}>Favorite</button>
      <button onClick={onUnfavorite}>Unfavorite</button>
      <span>{isFavorited ? 'Favorited' : 'Not Favorited'}</span>
    </div>
  )
}));

describe('RecommendationsPage', () => {
  it('renders and fetches recommendations on button click', async () => {
    render(
      <MemoryRouter>
        <RecommendationsPage />
      </MemoryRouter>
    );
    const btn = screen.getAllByRole('button', { name: /get recommendations/i });
    fireEvent.click(btn[1]);
    await waitFor(() => {
      expect(screen.getAllByText((content) => content.includes('Test Game')).length).toBeGreaterThan(0);
    });
  });
});
