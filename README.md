<h1 align="center">Get Ur Game!!!</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-20232A?style=for-the-badge&logo=python&logoColor=blue" alt="Python">
  <img src="https://img.shields.io/badge/django%20rest-ff1709?style=for-the-badge&logo=django&logoColor=white" alt="DRF">
  <img src="https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/redis-CC0000.svg?&style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/tailwind%20css-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS">
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

## Overview
**Get Ur Game!!!** is a game recommendation system that personalizes suggestions based on a user’s Steam library. The project includes both a frontend and backend to handle user interaction and provide recommendations.

---

## Features

- Fetches user’s owned games from Steam
- Neural network-based recommendation engine
- Backend APIs with Django REST and FastAPI
- Redis caching for performance
- Dockerized setup for easy deployment
- Beautiful frontend with React + Tailwind CSS
  
---

## Technologies

### Backend

#### Technologies
- **Django Rest Framework**: Framework for handling the backend logic, user authentication, and serving data.
- **Steam API**: Used to fetch user data (owned games) for recommendations.
- **Scikit-Learn**: A game recommendation system.


### Frontend

#### Technologies
- **React**: For building the user interface and managing application state.
- **Tailwind CSS**: For utility-first styling to create a responsive, modern UI.

---

## Setup & Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/get-ur-game.git
   cd get-ur-game
   ```

2. **Copy environment variables**
   Create a .env file in the root (or wherever needed by docker-compose.yml) and fill in required values:

   ```bash
    cp .env.example .env
   ```

3. **Build and start the containers**
   ```bash
   docker-compose up --build
   ```
   This command will:
   - Build all images (frontend, backend, ML service, etc.)
   - Start all containers (Django, FastAPI, PostgreSQL, Redis, etc.)

**How to access the app?**

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Prediction API: http://localhost:8080
