# Game Recommendation System

This service provides game recommendations based on a user's Steam library using a RandomForest classifier.

## Features

- Content-based filtering using genre probabilities from a RandomForest model
- Memory-optimized implementation that processes games in batches
- Weighted random sampling to provide varied recommendations on each request
- Cosine similarity to find games with similar genre profiles
- Prevention of repeated recommendations through a cooldown system

## How It Works

1. **User Profile Creation**: The system calculates a user profile based on the average genre probabilities of the user's owned games.

2. **Candidate Selection**: Instead of always selecting the top 5 most similar games, the system:
   - Collects a larger pool of candidate recommendations (up to 30 games)
   - Stores similarity scores for each candidate

3. **Weighted Random Sampling**: The system selects 5 games from the candidate pool using weighted random sampling:
   - Games with higher similarity scores have a higher probability of being selected
   - This ensures recommendations are still relevant but vary on each request

4. **Memory Optimization**: The system processes games in smaller batches to limit memory usage.

5. **Recommendation Cooldown**: The system prevents the same game from being recommended multiple times in a row:
   - Tracks recently recommended games for each user
   - Applies a 3-day cooldown period before a game can be recommended again
   - Automatically cleans up old entries to maintain memory efficiency

## API Endpoints

### POST /recommend/

Recommends games based on a list of game names.

**Request Body**:
```json
{
  "game_names": ["Game 1", "Game 2", "Game 3", ...],
  "user_id": "optional_user_identifier"  // Optional: Used to track recommendations per user
}
```

**Response**:
```json
{
  "recommendations": [
    {
      "name": "Recommended Game 1",
      "short_description": "Game description...",
      "header_image": "URL to game image",
      "appid": 12345
    },
    ...
  ]
}
```

## Recent Changes

- Added weighted random sampling to provide varied recommendations on each request
- Increased the candidate pool size to 50 games
- Added explicit random seed initialization to ensure different recommendations on each run
- Implemented a recommendation cooldown system to prevent the same game from being recommended multiple times in a row
- Added user tracking to personalize recommendation history
- Added a 3-day cooldown period before a game can be recommended again to the same user
