// Pickleball App JavaScript

// Global variables
let currentUser = null;
let authToken = null;
let chatSocket = null;

// API base URL
const API_BASE_URL = "/api";

// DOM Elements
const loginBtn = document.getElementById("login-btn");
const registerBtn = document.getElementById("register-btn");
const logoutBtn = document.getElementById("logout-btn");
const authButtons = document.getElementById("auth-buttons");
const userProfile = document.getElementById("user-profile");
const usernameDisplay = document.getElementById("username-display");
const mainContent = document.getElementById("main-content");
const viewGamesBtn = document.getElementById("view-games-btn");
const scheduleGameBtn = document.getElementById("schedule-game-btn");

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  // Check if user is logged in
  checkAuthStatus();

  // Set up event listeners
  setupEventListeners();
});

// Check authentication status
function checkAuthStatus() {
  const token = localStorage.getItem("authToken");
  if (token) {
    authToken = token;
    fetchUserProfile();
  }
}

// Set up event listeners
function setupEventListeners() {
  // Auth buttons
  loginBtn.addEventListener("click", showLoginModal);
  registerBtn.addEventListener("click", showRegisterModal);
  logoutBtn.addEventListener("click", logout);

  // Navigation buttons
  viewGamesBtn.addEventListener("click", () => navigateTo("games"));
  scheduleGameBtn.addEventListener("click", () => navigateTo("schedule-game"));

  // Forms
  document.getElementById("login-form").addEventListener("submit", handleLogin);
  document
    .getElementById("register-form")
    .addEventListener("submit", handleRegister);
}

// Show login modal
function showLoginModal() {
  const loginModal = new bootstrap.Modal(
    document.getElementById("login-modal")
  );
  loginModal.show();
}

// Show register modal
function showRegisterModal() {
  const registerModal = new bootstrap.Modal(
    document.getElementById("register-modal")
  );
  registerModal.show();
}

// Handle login form submission
async function handleLogin(event) {
  event.preventDefault();

  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;
  const errorElement = document.getElementById("login-error");

  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Login failed");
    }

    // Store auth token and user data
    authToken = data.access_token;
    currentUser = data.user;

    // Save token to local storage
    localStorage.setItem("authToken", authToken);

    // Update UI
    updateAuthUI();

    // Close modal
    bootstrap.Modal.getInstance(document.getElementById("login-modal")).hide();

    // Navigate to games page
    navigateTo("games");
  } catch (error) {
    errorElement.textContent = error.message;
    errorElement.classList.remove("d-none");
  }
}

// Handle register form submission
async function handleRegister(event) {
  event.preventDefault();

  const username = document.getElementById("register-username").value;
  const email = document.getElementById("register-email").value;
  const password = document.getElementById("register-password").value;
  const confirmPassword = document.getElementById(
    "register-confirm-password"
  ).value;
  const errorElement = document.getElementById("register-error");

  // Validate passwords match
  if (password !== confirmPassword) {
    errorElement.textContent = "Passwords do not match";
    errorElement.classList.remove("d-none");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Registration failed");
    }

    // Store auth token and user data
    authToken = data.access_token;
    currentUser = data.user;

    // Save token to local storage
    localStorage.setItem("authToken", authToken);

    // Update UI
    updateAuthUI();

    // Close modal
    bootstrap.Modal.getInstance(
      document.getElementById("register-modal")
    ).hide();

    // Navigate to games page
    navigateTo("games");
  } catch (error) {
    errorElement.textContent = error.message;
    errorElement.classList.remove("d-none");
  }
}

// Fetch user profile
async function fetchUserProfile() {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch user profile");
    }

    const data = await response.json();
    currentUser = data.user;

    // Update UI
    updateAuthUI();
  } catch (error) {
    console.error("Error fetching user profile:", error);
    logout();
  }
}

// Update authentication UI
function updateAuthUI() {
  if (currentUser) {
    authButtons.classList.add("d-none");
    userProfile.classList.remove("d-none");
    usernameDisplay.textContent = currentUser.username;
  } else {
    authButtons.classList.remove("d-none");
    userProfile.classList.add("d-none");
    usernameDisplay.textContent = "";
  }
}

// Logout
function logout() {
  // Clear auth data
  authToken = null;
  currentUser = null;
  localStorage.removeItem("authToken");

  // Update UI
  updateAuthUI();

  // Navigate to home
  navigateTo("home");

  // Close WebSocket connection if open
  if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    chatSocket.close();
  }
}

// Load court details page
async function loadCourtDetailsPage(courtId) {
  if (!courtId) {
    navigateTo("courts");
    return;
  }

  mainContent.innerHTML = `
    <div class="container">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  `;

  try {
    const response = await fetch(`${API_BASE_URL}/courts/${courtId}`);
    if (!response.ok) {
      throw new Error("Failed to load court details");
    }
    const court = await response.json();

    // Now fetch games scheduled at this court
    const gamesResponse = await fetch(
      `${API_BASE_URL}/games?court_id=${courtId}`
    );
    if (!gamesResponse.ok) {
      throw new Error("Failed to load games for this court");
    }
    const gamesData = await gamesResponse.json();
    const games = gamesData.games || [];

    mainContent.innerHTML = `
      <div class="container">
        <div class="row mb-4">
          <div class="col-md-8">
            <h1>${court.name}</h1>
            <p class="lead">${court.address}</p>
            ${
              court.court_type
                ? `<p><strong>Type:</strong> ${court.court_type}</p>`
                : ""
            }
            ${
              court.surface_type
                ? `<p><strong>Surface:</strong> ${court.surface_type}</p>`
                : ""
            }
            ${
              court.number_of_courts
                ? `<p><strong>Number of courts:</strong> ${court.number_of_courts}</p>`
                : ""
            }
            ${
              court.rating
                ? `<p><strong>Rating:</strong> ${court.rating} (${court.total_ratings} ratings)</p>`
                : ""
            }
            ${
              court.phone ? `<p><strong>Phone:</strong> ${court.phone}</p>` : ""
            }
            ${
              court.website
                ? `<p><strong>Website:</strong> <a href="${court.website}" target="_blank">${court.website}</a></p>`
                : ""
            }
          </div>
          <div class="col-md-4 text-md-end mt-3 mt-md-0">
            <button class="btn btn-primary btn-lg" onclick="navigateTo('schedule-game', ${courtId})">
              Schedule a Game
            </button>
          </div>
        </div>

        <h2 class="mt-5 mb-4">Upcoming Games</h2>
        <div class="row" id="court-games-container">
          ${
            games.length === 0
              ? `<div class="col-12"><p>No games scheduled at this court yet.</p></div>`
              : games
                  .map(
                    (game) => `
                <div class="col-md-6 col-lg-4 mb-4">
                  <div class="card game-card">
                    <div class="card-body">
                      <h5 class="card-title">Game on ${new Date(
                        game.date
                      ).toLocaleDateString()}</h5>
                      <p><strong>Time:</strong> ${new Date(
                        `2000-01-01T${game.time}`
                      ).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}</p>
                      <p><strong>Skill Level:</strong> ${
                        game.skill_level || "Any"
                      }</p>
                      <p><strong>Players:</strong> ${
                        game.participants.length
                      }/${game.max_players}</p>
                      <button class="btn btn-primary mt-2" onclick="navigateTo('game-details', ${
                        game.game_id
                      })">
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              `
                  )
                  .join("")
          }
        </div>
      </div>
    `;
  } catch (error) {
    console.error("Error loading court details:", error);
    mainContent.innerHTML = `
      <div class="container">
        <div class="alert alert-danger" role="alert">
          Failed to load court details. Please try again later.
        </div>
        <button class="btn btn-primary" onclick="navigateTo('courts')">Back to Courts</button>
      </div>
    `;
  }
}

// Load schedule game form
function loadScheduleGameForm(courtId = null) {
  if (!authToken) {
    showLoginModal();
    return;
  }

  let courtSelectionHtml =
    '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading courts...</span></div>';

  mainContent.innerHTML = `
    <div class="container">
      <h1 class="mb-4">Schedule a Game</h1>
      <form id="schedule-game-form">
        <div class="mb-3">
          <label for="court-select" class="form-label">Court</label>
          <div id="court-selection-container">
            ${courtSelectionHtml}
          </div>
        </div>
        <div class="mb-3">
          <label for="game-date" class="form-label">Date</label>
          <input type="date" class="form-control" id="game-date" required min="${
            new Date().toISOString().split("T")[0]
          }">
        </div>
        <div class="mb-3">
          <label for="game-time" class="form-label">Time</label>
          <input type="time" class="form-control" id="game-time" required>
        </div>
        <div class="mb-3">
          <label for="max-players" class="form-label">Maximum Players</label>
          <select class="form-control" id="max-players">
            <option value="2">2</option>
            <option value="4" selected>4</option>
            <option value="6">6</option>
            <option value="8">8</option>
            <option value="12">12</option>
            <option value="16">16</option>
          </select>
        </div>
        <div class="mb-3">
          <label for="skill-level" class="form-label">Skill Level</label>
          <select class="form-control" id="skill-level">
            <option value="">Any</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
        <div class="mb-3">
          <label for="game-notes" class="form-label">Notes</label>
          <textarea class="form-control" id="game-notes" rows="3" placeholder="Additional information about the game..."></textarea>
        </div>
        <button type="submit" class="btn btn-primary">Schedule Game</button>
        <button type="button" class="btn btn-secondary" onclick="navigateTo('courts')">Cancel</button>
      </form>
    </div>
  `;

  // Fetch courts for the selection dropdown
  fetch(`${API_BASE_URL}/courts`)
    .then((response) => response.json())
    .then((data) => {
      const courtsContainer = document.getElementById(
        "court-selection-container"
      );
      if (data.courts && data.courts.length > 0) {
        let selectHtml = `<select class="form-control" id="court-select" required>`;
        data.courts.forEach((court) => {
          const selected =
            court.court_id === parseInt(courtId) ? "selected" : "";
          selectHtml += `<option value="${court.court_id}" ${selected}>${court.name}</option>`;
        });
        selectHtml += `</select>`;
        courtsContainer.innerHTML = selectHtml;
      } else {
        courtsContainer.innerHTML =
          '<div class="alert alert-warning">No courts available. Please add courts first.</div>';
      }
    })
    .catch((error) => {
      console.error("Error fetching courts:", error);
      const courtsContainer = document.getElementById(
        "court-selection-container"
      );
      courtsContainer.innerHTML =
        '<div class="alert alert-danger">Failed to load courts. Please try again later.</div>';
    });

  // Add event listener for form submission
  document
    .getElementById("schedule-game-form")
    .addEventListener("submit", handleScheduleGame);
}

// Handle game scheduling form submission
async function handleScheduleGame(event) {
  event.preventDefault();

  if (!authToken) {
    showLoginModal();
    return;
  }

  const courtSelect = document.getElementById("court-select");
  const gameDate = document.getElementById("game-date");
  const gameTime = document.getElementById("game-time");
  const maxPlayers = document.getElementById("max-players");
  const skillLevel = document.getElementById("skill-level");
  const gameNotes = document.getElementById("game-notes");

  if (!courtSelect || !gameDate || !gameTime) {
    alert("Please fill all required fields");
    return;
  }

  // Validate that a court is selected
  if (!courtSelect.value) {
    alert("Please select a court");
    return;
  }

  // Validate date and time
  const selectedDate = new Date(gameDate.value);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (selectedDate < today) {
    alert("Game date cannot be in the past");
    return;
  }

  const gameData = {
    court_id: parseInt(courtSelect.value),
    date: gameDate.value, // Format: YYYY-MM-DD
    time: gameTime.value, // Format: HH:MM
    max_players: parseInt(maxPlayers.value),
    skill_level: skillLevel.value,
    notes: gameNotes.value || "",
  };

  console.log("Scheduling game with data:", gameData);

  try {
    const response = await fetch(`${API_BASE_URL}/games`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify(gameData),
    });

    // Parse JSON response data only once
    const responseData = await response.json();

    if (!response.ok) {
      console.error("Server error response:", responseData);
      throw new Error(responseData.message || "Failed to schedule game");
    }

    console.log("Game scheduled successfully:", responseData);
    alert("Game scheduled successfully!");

    // Navigate to the game details page with the new game ID
    if (responseData.game_id) {
      navigateTo("game-details", responseData.game_id);
    } else if (responseData.game && responseData.game.game_id) {
      navigateTo("game-details", responseData.game.game_id);
    } else {
      console.warn("Game ID not found in response:", responseData);
      navigateTo("games"); // Fallback to games list
    }
  } catch (error) {
    console.error("Error scheduling game:", error);
    alert(`Error scheduling game: ${error.message}`);
  }
}

// Navigation
function navigateTo(page, id = null) {
  console.log(`Navigating to ${page} with id ${id}`);

  // Disconnect from WebSocket when navigating away from a game chat
  if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    chatSocket.close();
    chatSocket = null;
  }

  try {
    switch (page) {
      case "home":
        console.log("Loading home page");
        loadHomePage();
        break;
      case "games":
        console.log("Loading games page");
        loadGamesPage();
        break;
      case "game-details":
        console.log("Loading game details page");
        loadGameDetailsPage(id);
        break;
      case "courts":
        console.log("Loading courts page");
        loadCourtsPage();
        break;
      case "court-details":
        console.log("Loading court details page");
        loadCourtDetailsPage(id);
        break;
      case "schedule-game":
      case "schedule-game-page":
        console.log("Loading schedule game form");
        if (id) {
          loadScheduleGameForm(id); // Schedule at a specific court
        } else {
          loadScheduleGameForm(); // General scheduling form
        }
        break;
      default:
        console.log("Loading default home page");
        loadHomePage();
    }
  } catch (error) {
    console.error(`Error navigating to ${page}:`, error);
  }
}

// Load home page
function loadHomePage() {
  mainContent.innerHTML = `
        <div class="text-center py-5">
            <h1>Welcome to the Pickleball App</h1>
            <p class="lead">Schedule games, find courts, and chat with other players</p>
            <div class="mt-4">
                <button class="btn btn-primary btn-lg me-2" id="view-games-btn">View Games</button>
                <button class="btn btn-success btn-lg" id="schedule-game-btn">Schedule a Game</button>
            </div>
        </div>
    `;

  // Re-attach event listeners
  document
    .getElementById("view-games-btn")
    .addEventListener("click", () => navigateTo("games"));
  document
    .getElementById("schedule-game-btn")
    .addEventListener("click", () => navigateTo("schedule-game"));
}

// Load games page
function loadGamesPage() {
  mainContent.innerHTML = `
    <div class="row mb-4">
      <div class="col">
        <h2>Pickleball Games</h2>
        <button class="btn btn-success" id="new-game-btn">Schedule New Game</button>
      </div>
    </div>
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="input-group">
          <input type="text" class="form-control" id="game-search" placeholder="Search games">
          <button class="btn btn-primary" id="search-games-btn">Search</button>
        </div>
      </div>
      <div class="col-md-4">
        <button class="btn btn-success w-100" id="search-games-near-me-btn">
          <i class="bi bi-geo-alt"></i> Games Near Me
        </button>
      </div>
    </div>
    <div class="row mb-3" id="games-radius-controls" style="display: none;">
      <div class="col-md-8">
        <label for="games-radius-slider" class="form-label">Search Radius: <span id="games-radius-value">10</span> km</label>
        <input type="range" class="form-range" id="games-radius-slider" min="1" max="50" value="10">
      </div>
    </div>
    <div class="row mb-3">
      <div class="col-md-4">
        <select class="form-select" id="filter-status">
          <option value="">All Status</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      <div class="col-md-4">
        <select class="form-select" id="filter-skill">
          <option value="">All Skill Levels</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
          <option value="all levels">All Levels</option>
        </select>
      </div>
    </div>
    <div class="row" id="games-container">
      <div class="col-12 text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  `;

  document.getElementById("new-game-btn").addEventListener("click", () => {
    navigateTo("schedule-game");
  });

  document
    .getElementById("filter-status")
    .addEventListener("change", fetchGames);
  document
    .getElementById("filter-skill")
    .addEventListener("change", fetchGames);

  document
    .getElementById("search-games-btn")
    .addEventListener("click", searchGames);
  document.getElementById("game-search").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      searchGames();
    }
  });

  // Near me search functionality for games
  const searchGamesNearMeBtn = document.getElementById(
    "search-games-near-me-btn"
  );
  const gamesRadiusControls = document.getElementById("games-radius-controls");
  const gamesRadiusSlider = document.getElementById("games-radius-slider");
  const gamesRadiusValue = document.getElementById("games-radius-value");

  searchGamesNearMeBtn.addEventListener("click", () => {
    getUserLocation((position) => {
      gamesRadiusControls.style.display = "block";
      searchGamesByLocation(
        position.coords.latitude,
        position.coords.longitude,
        gamesRadiusSlider.value
      );
    });
  });

  gamesRadiusSlider.addEventListener("input", () => {
    gamesRadiusValue.textContent = gamesRadiusSlider.value;
  });

  gamesRadiusSlider.addEventListener("change", () => {
    if (currentUserLocation) {
      searchGamesByLocation(
        currentUserLocation.latitude,
        currentUserLocation.longitude,
        gamesRadiusSlider.value
      );
    }
  });

  // Fetch and display games
  fetchGames();
}

// Global variable to store user location
let currentUserLocation = null;

// Get user's current location
function getUserLocation(callback) {
  if (navigator.geolocation) {
    // Find the button that was clicked (either near courts or near games)
    const searchNearMeBtn =
      document.getElementById("search-near-me-btn") ||
      document.getElementById("search-games-near-me-btn");

    if (!searchNearMeBtn) {
      console.error("Could not find the search near me button");
      alert("Error initializing location search. Please try again.");
      return;
    }

    // Display loading state
    const originalBtnText = searchNearMeBtn.innerHTML;
    searchNearMeBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Getting location...`;
    searchNearMeBtn.disabled = true;

    navigator.geolocation.getCurrentPosition(
      (position) => {
        // Success
        currentUserLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        };

        // Restore button state
        searchNearMeBtn.innerHTML = originalBtnText;
        searchNearMeBtn.disabled = false;

        // Call the callback with the location data
        callback(position);
      },
      (error) => {
        // Error
        console.error("Error getting location:", error);
        searchNearMeBtn.innerHTML = originalBtnText;
        searchNearMeBtn.disabled = false;

        // Show error message
        alert(
          `Unable to get your location: ${error.message}. Please try again or search manually.`
        );
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  } else {
    alert(
      "Geolocation is not supported by your browser. Please search manually."
    );
  }
}

// Search games by location
async function searchGamesByLocation(lat, lng, radius = 10) {
  const gamesContainer = document.getElementById("games-container");
  gamesContainer.innerHTML = `
    <div class="col-12 text-center">
        <div class="spinner-border" role="status">
            <span class="visually-hidden">Searching...</span>
        </div>
    </div>
  `;

  try {
    const response = await fetch(
      `${API_BASE_URL}/search/games?lat=${lat}&lng=${lng}&radius=${radius}`
    );

    if (!response.ok) {
      throw new Error("Location search failed");
    }

    const data = await response.json();

    if (!data.games || data.games.length === 0) {
      gamesContainer.innerHTML = `
        <div class="col-12 text-center">
            <p>No games found within ${radius} km of your location.</p>
            <button class="btn btn-primary" onclick="loadGamesPage()">Show All Games</button>
        </div>
      `;
      return;
    }

    gamesContainer.innerHTML = `
      <div class="col-12 mb-3">
        <div class="alert alert-info">
          Showing ${data.games.length} games within ${radius} km of your location
        </div>
      </div>
    `;

    // Render the games
    renderGames(data.games);
  } catch (error) {
    console.error("Error searching games by location:", error);
    gamesContainer.innerHTML = `
      <div class="col-12 text-center">
          <p class="text-danger">Error searching for games: ${error.message}</p>
          <button class="btn btn-primary" onclick="loadGamesPage()">Show All Games</button>
      </div>
    `;
  }
}

// Modified function to render games with optional distance information
function renderGames(games) {
  const gamesContainer = document.getElementById("games-container");

  if (games.length === 0) {
    gamesContainer.innerHTML = `
        <div class="col-12 text-center">
            <p>No games found matching your criteria.</p>
        </div>
    `;
    return;
  }

  // Clear previous content if not already done
  if (!gamesContainer.querySelector(".alert")) {
    gamesContainer.innerHTML = "";
  }

  games.forEach((game) => {
    const gameCard = document.createElement("div");
    gameCard.className = "col-lg-6 mb-4";

    // Format date and time
    const gameDate = new Date(game.scheduled_time);
    const formattedDate = gameDate.toLocaleDateString();
    const formattedTime = gameDate.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    // Status badge color
    let statusBadgeClass = "bg-secondary";
    if (game.status === "open") statusBadgeClass = "bg-success";
    if (game.status === "in_progress") statusBadgeClass = "bg-primary";
    if (game.status === "completed") statusBadgeClass = "bg-info";
    if (game.status === "cancelled") statusBadgeClass = "bg-danger";

    // Players info
    const maxPlayers = game.max_players || 4;
    const currentPlayers = game.players ? game.players.length : 1; // At least creator

    gameCard.innerHTML = `
      <div class="card h-100">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>${game.court ? game.court.name : "Court not specified"}</span>
          <span class="badge ${statusBadgeClass}">${game.status}</span>
        </div>
        <div class="card-body">
          <h5 class="card-title">
            ${formattedDate} at ${formattedTime}
            ${
              game.skill_level
                ? `<span class="badge bg-secondary">${game.skill_level}</span>`
                : ""
            }
          </h5>
          <div class="card-text">
            <p>${game.notes || "No additional notes"}</p>
            <div class="progress mb-3" style="height: 25px;">
              <div class="progress-bar bg-success" role="progressbar" 
                style="width: ${(currentPlayers / maxPlayers) * 100}%;" 
                aria-valuenow="${currentPlayers}" aria-valuemin="0" aria-valuemax="${maxPlayers}">
                ${currentPlayers}/${maxPlayers} Players
              </div>
            </div>
            ${
              game.distance
                ? `<p class="text-success"><strong>${game.distance} km away</strong></p>`
                : ""
            }
          </div>
        </div>
        <div class="card-footer">
          <button class="btn btn-primary" onclick="navigateTo('game-details', ${
            game.game_id
          })">
            View Details
          </button>
        </div>
      </div>
    `;

    gamesContainer.appendChild(gameCard);
  });
}

// Modify the existing fetchGames function to use renderGames
async function fetchGames() {
  const gamesContainer = document.getElementById("games-container");
  const statusFilter = document.getElementById("filter-status").value;
  const skillFilter = document.getElementById("filter-skill").value;

  gamesContainer.innerHTML = `
    <div class="col-12 text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  `;

  try {
    let url = `${API_BASE_URL}/games`;
    const queryParams = [];

    if (statusFilter) {
      queryParams.push(`status=${statusFilter}`);
    }

    if (skillFilter) {
      queryParams.push(`skill_level=${skillFilter}`);
    }

    if (queryParams.length > 0) {
      url += `?${queryParams.join("&")}`;
    }

    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to fetch games");
    }

    // Use the new renderGames function
    renderGames(data.games);
  } catch (error) {
    console.error("Error fetching games:", error);
    gamesContainer.innerHTML = `
      <div class="col-12">
        <div class="alert alert-danger">
          Error loading games: ${error.message}
        </div>
      </div>
    `;
  }
}

// Update searchGames to use renderGames
async function searchGames() {
  const searchTerm = document.getElementById("game-search").value.trim();

  if (!searchTerm) {
    loadGamesPage();
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/search/games?q=${encodeURIComponent(searchTerm)}`
    );
    const data = await response.json();

    const gamesContainer = document.getElementById("games-container");

    if (!response.ok) {
      throw new Error(data.message || "Search failed");
    }

    if (data.games.length === 0) {
      gamesContainer.innerHTML = `
                <div class="col-12 text-center">
                    <p>No games found matching "${searchTerm}"</p>
                    <button class="btn btn-primary" id="clear-search-btn">Clear Search</button>
                </div>
            `;
      document
        .getElementById("clear-search-btn")
        .addEventListener("click", () => {
          document.getElementById("game-search").value = "";
          loadGamesPage();
        });
      return;
    }

    gamesContainer.innerHTML = "";

    // Use the new renderGames function
    renderGames(data.games);
  } catch (error) {
    console.error("Error searching games:", error);
    const gamesContainer = document.getElementById("games-container");
    gamesContainer.innerHTML = `
      <div class="col-12">
        <div class="alert alert-danger">
          Error searching games: ${error.message}
        </div>
      </div>
    `;
  }
}

// Load game details page
async function loadGameDetailsPage(gameId) {
  if (!gameId) {
    navigateTo("games");
    return;
  }

  mainContent.innerHTML = `
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading game details...</span>
            </div>
        </div>
    `;

  try {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to load game details");
    }

    const game = data.game;
    const gameDate = new Date(game.date);
    const formattedDate = gameDate.toLocaleDateString();
    const gameTime = game.time ? game.time.substring(0, 5) : "TBD";

    // Check if user is a participant
    const isParticipant =
      currentUser &&
      game.participants &&
      game.participants.some((p) => p.user_id === currentUser.user_id);

    // Check if game is full
    const isFull =
      game.participants && game.participants.length >= game.max_players;

    mainContent.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <h1 class="mb-3">Game Details</h1>
                    <div class="card mb-4">
                        <div class="card-body">
                            <h5 class="card-title">${formattedDate} at ${gameTime}</h5>
                            <p class="card-text">
                                <strong>Court:</strong> ${
                                  game.court ? game.court.name : "Court TBD"
                                }<br>
                                <strong>Skill Level:</strong> ${
                                  game.skill_level || "Not specified"
                                }<br>
                                <strong>Players:</strong> ${
                                  game.participants
                                    ? game.participants.length
                                    : 0
                                }/${game.max_players}<br>
                                <strong>Status:</strong> ${
                                  game.status.charAt(0).toUpperCase() +
                                  game.status.slice(1)
                                }<br>
                                <strong>Notes:</strong> ${
                                  game.notes || "No notes provided"
                                }
                            </p>
                            <div class="mt-3">
                                ${
                                  !currentUser
                                    ? `
                                    <button class="btn btn-primary" id="login-to-join-btn">Login to Join</button>
                                `
                                    : isParticipant
                                    ? `
                                    <button class="btn btn-danger" id="leave-game-btn">Leave Game</button>
                                `
                                    : isFull
                                    ? `
                                    <button class="btn btn-secondary" disabled>Game is Full</button>
                                `
                                    : `
                                    <button class="btn btn-success" id="join-game-btn">Join Game</button>
                                `
                                }
                                <button class="btn btn-outline-primary" id="back-to-games-btn">Back to Games</button>
                            </div>
                        </div>
                    </div>
                    
                    <h3>Participants</h3>
                    <div class="card mb-4">
                        <div class="card-body">
                            <ul class="list-group list-group-flush" id="participants-list">
                                ${
                                  game.participants &&
                                  game.participants.length > 0
                                    ? game.participants
                                        .map(
                                          (p) => `
                                        <li class="list-group-item">
                                            <strong>${
                                              p.username || "Unknown User"
                                            }</strong>
                                            <small class="text-muted">Joined: ${new Date(
                                              p.joined_at
                                            ).toLocaleString()}</small>
                                        </li>
                                    `
                                        )
                                        .join("")
                                    : '<li class="list-group-item">No participants yet</li>'
                                }
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <h3>Game Chat</h3>
                    ${
                      isParticipant
                        ? `
                        <div id="chat-connection-status" class="chat-connection-status connecting">
                            Connecting to chat...
                        </div>
                        <div class="chat-container mb-3" id="chat-messages"></div>
                        <div class="chat-input-container">
                            <input type="text" class="form-control chat-input" id="chat-input" placeholder="Type a message...">
                            <button class="btn btn-primary send-message-btn" id="send-message-btn">
                                <i class="bi bi-send"></i>
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-send" viewBox="0 0 16 16">
                                    <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576 6.636 10.07Zm6.787-8.201L1.591 6.602l4.339 2.76 7.494-7.493Z"/>
                                </svg>
                            </button>
                        </div>
                    `
                        : `
                        <div class="alert alert-info">
                            Join the game to participate in the chat.
                        </div>
                    `
                    }
                </div>
            </div>
        `;

    // Add event listeners
    document
      .getElementById("back-to-games-btn")
      .addEventListener("click", () => navigateTo("games"));

    if (!currentUser) {
      document
        .getElementById("login-to-join-btn")
        .addEventListener("click", showLoginModal);
    } else if (isParticipant) {
      document
        .getElementById("leave-game-btn")
        .addEventListener("click", () => leaveGame(gameId));

      // Set up chat
      loadGameChat(gameId);

      document
        .getElementById("send-message-btn")
        .addEventListener("click", () => sendChatMessage(gameId));
      document
        .getElementById("chat-input")
        .addEventListener("keyup", (event) => {
          if (event.key === "Enter") {
            sendChatMessage(gameId);
          }
        });
    } else if (!isFull) {
      document
        .getElementById("join-game-btn")
        .addEventListener("click", () => joinGame(gameId));
    }
  } catch (error) {
    console.error("Error loading game details:", error);
    mainContent.innerHTML = `
            <div class="text-center">
                <h1>Error</h1>
                <p class="text-danger">${error.message}</p>
                <button class="btn btn-primary" id="back-btn">Back to Games</button>
            </div>
        `;
    document
      .getElementById("back-btn")
      .addEventListener("click", () => navigateTo("games"));
  }
}

// Join a game
async function joinGame(gameId) {
  if (!currentUser || !authToken) {
    showLoginModal();
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/join`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to join game");
    }

    // Reload game details
    loadGameDetailsPage(gameId);
  } catch (error) {
    console.error("Error joining game:", error);
    alert(`Error joining game: ${error.message}`);
  }
}

// Leave a game
async function leaveGame(gameId) {
  if (!currentUser || !authToken) {
    showLoginModal();
    return;
  }

  if (!confirm("Are you sure you want to leave this game?")) {
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/leave`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to leave game");
    }

    // Close WebSocket connection if open
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
      chatSocket.close();
    }

    // Navigate back to games list
    navigateTo("games");
  } catch (error) {
    console.error("Error leaving game:", error);
    alert(`Error leaving game: ${error.message}`);
  }
}

// Load game chat
async function loadGameChat(gameId) {
  const chatContainer = document.getElementById("chat-messages");

  if (!chatContainer) {
    return;
  }

  chatContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading chat...</span>
            </div>
            <p>Loading chat messages...</p>
        </div>
    `;

  try {
    // Fetch chat history
    const response = await fetch(`${API_BASE_URL}/chat/games/${gameId}`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to load chat messages");
    }

    // Display chat messages
    displayChatMessages(data.messages, chatContainer);

    // Connect to WebSocket for real-time chat
    connectToChat(gameId);
  } catch (error) {
    console.error("Error loading chat:", error);
    chatContainer.innerHTML = `
            <div class="alert alert-danger">
                Error loading chat: ${error.message}
                <button class="btn btn-sm btn-outline-danger" id="retry-chat-btn">Retry</button>
            </div>
        `;
    document
      .getElementById("retry-chat-btn")
      .addEventListener("click", () => loadGameChat(gameId));
  }
}

// Display chat messages
function displayChatMessages(messages, container) {
  if (!messages || messages.length === 0) {
    container.innerHTML = `<p class="text-center text-muted">No messages yet. Be the first to say hello!</p>`;
    return;
  }

  container.innerHTML = "";

  messages.forEach((message) => {
    const isCurrentUser =
      currentUser && message.user_id === currentUser.user_id;
    const messageElement = document.createElement("div");
    messageElement.className = `chat-message ${
      isCurrentUser ? "sent" : "received"
    }`;

    messageElement.innerHTML = `
            <div class="chat-username">${
              message.username || "Unknown User"
            }</div>
            <div class="chat-content">${message.message_text}</div>
            <div class="chat-timestamp">${new Date(
              message.timestamp
            ).toLocaleTimeString()}</div>
        `;

    container.appendChild(messageElement);
  });

  // Scroll to bottom
  container.scrollTop = container.scrollHeight;
}

// Connect to WebSocket chat
function connectToChat(gameId) {
  // Close existing connection if any
  if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    chatSocket.close();
  }

  const connectionStatus = document.getElementById("chat-connection-status");
  if (connectionStatus) {
    connectionStatus.className = "chat-connection-status connecting";
    connectionStatus.textContent = "Connecting to chat...";
  }

  // Get WebSocket URL from environment
  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsHost = window.location.hostname;
  const wsPort = 8765; // This should match the port in your WebSocket server

  const wsUrl = `${wsProtocol}//${wsHost}:${wsPort}`;

  // Create new WebSocket connection
  try {
    chatSocket = new WebSocket(wsUrl);

    chatSocket.onopen = () => {
      console.log("WebSocket connection established");
      if (connectionStatus) {
        connectionStatus.className = "chat-connection-status connected";
        connectionStatus.textContent = "Connected to chat";
      }

      // Authenticate with the WebSocket server
      chatSocket.send(
        JSON.stringify({
          game_id: gameId,
          user_id: currentUser.user_id,
          token: authToken,
        })
      );
    };

    chatSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "chat") {
        // Add new message to chat
        const chatContainer = document.getElementById("chat-messages");
        if (chatContainer) {
          const isCurrentUser = data.user_id === currentUser.user_id;
          const messageElement = document.createElement("div");
          messageElement.className = `chat-message ${
            isCurrentUser ? "sent" : "received"
          }`;

          messageElement.innerHTML = `
            <div class="chat-username">${data.username || "Unknown User"}</div>
            <div class="chat-content">${data.message}</div>
            <div class="chat-timestamp">${new Date().toLocaleTimeString()}</div>
          `;

          chatContainer.appendChild(messageElement);
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      } else if (data.type === "user_joined") {
        // Update UI to show a user joined
        const chatContainer = document.getElementById("chat-messages");
        if (chatContainer) {
          const systemMessage = document.createElement("div");
          systemMessage.className = "text-center text-muted my-2";
          systemMessage.innerHTML = `<small>A user has joined the chat</small>`;
          chatContainer.appendChild(systemMessage);
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      } else if (data.type === "user_left") {
        // Update UI to show a user left
        const chatContainer = document.getElementById("chat-messages");
        if (chatContainer) {
          const systemMessage = document.createElement("div");
          systemMessage.className = "text-center text-muted my-2";
          systemMessage.innerHTML = `<small>A user has left the chat</small>`;
          chatContainer.appendChild(systemMessage);
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      }
    };

    chatSocket.onclose = () => {
      console.log("WebSocket connection closed");
      if (connectionStatus) {
        connectionStatus.className = "chat-connection-status disconnected";
        connectionStatus.textContent = "Disconnected from chat";
      }
    };

    chatSocket.onerror = (error) => {
      console.error("WebSocket error:", error);
      if (connectionStatus) {
        connectionStatus.className = "chat-connection-status disconnected";
        connectionStatus.textContent = "Error connecting to chat";
      }
    };
  } catch (error) {
    console.error("Error creating WebSocket:", error);
    if (connectionStatus) {
      connectionStatus.className = "chat-connection-status disconnected";
      connectionStatus.textContent = "Error connecting to chat";
    }
  }
}

// Send chat message
function sendChatMessage(gameId) {
  const chatInput = document.getElementById("chat-input");
  if (!chatInput || !chatInput.value.trim()) {
    return;
  }

  const message = chatInput.value.trim();
  chatInput.value = "";

  // Optimistically add the message to the UI
  const chatContainer = document.getElementById("chat-messages");
  if (chatContainer) {
    const messageElement = document.createElement("div");
    messageElement.className = "chat-message sent";
    messageElement.innerHTML = `
      <div class="chat-username">${currentUser.username}</div>
      <div class="chat-content">${message}</div>
      <div class="chat-timestamp">${new Date().toLocaleTimeString()}</div>
    `;
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // Try to send via WebSocket first
  if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    chatSocket.send(
      JSON.stringify({
        type: "chat",
        game_id: gameId,
        user_id: currentUser.user_id,
        message: message,
      })
    );
  } else {
    // Fall back to API if WebSocket is not connected
    sendChatMessageViaAPI(gameId, message);
  }
}

// Send chat message via API (fallback)
async function sendChatMessageViaAPI(gameId, message) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/games/${gameId}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to send message");
    }

    // Reload chat messages
    loadGameChat(gameId);
  } catch (error) {
    console.error("Error sending message:", error);
    alert(`Error sending message: ${error.message}`);
  }
}

// Load courts page
function loadCourtsPage() {
  mainContent.innerHTML = `
    <div class="row mb-4">
      <div class="col">
        <h2>Pickleball Courts</h2>
      </div>
    </div>
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="input-group">
          <input type="text" class="form-control" id="court-search" placeholder="Search courts by name">
          <button class="btn btn-primary" id="search-courts-btn">Search</button>
        </div>
      </div>
      <div class="col-md-4">
        <button class="btn btn-success w-100" id="search-near-me-btn">
          <i class="bi bi-geo-alt"></i> Search Near Me
        </button>
      </div>
    </div>
    <div class="row mb-3" id="radius-controls" style="display: none;">
      <div class="col-md-8">
        <label for="radius-slider" class="form-label">Search Radius: <span id="radius-value">10</span> km</label>
        <input type="range" class="form-range" id="radius-slider" min="1" max="50" value="10">
      </div>
    </div>
    <div class="row" id="courts-container">
      <div class="col-12 text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  `;

  // Fetch courts and render
  fetchCourts();

  // Set up event listeners
  document.getElementById("search-courts-btn").addEventListener("click", () => {
    const query = document.getElementById("court-search").value.trim();
    searchCourts(query);
  });

  document.getElementById("court-search").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      const query = document.getElementById("court-search").value.trim();
      searchCourts(query);
    }
  });

  // Near me search functionality
  const searchNearMeBtn = document.getElementById("search-near-me-btn");
  const radiusControls = document.getElementById("radius-controls");
  const radiusSlider = document.getElementById("radius-slider");
  const radiusValue = document.getElementById("radius-value");

  searchNearMeBtn.addEventListener("click", () => {
    getUserLocation((location) => {
      radiusControls.style.display = "block";
      searchCourtsByLocation(
        location.coords.latitude,
        location.coords.longitude,
        radiusSlider.value
      );
    });
  });

  radiusSlider.addEventListener("input", () => {
    radiusValue.textContent = radiusSlider.value;
  });

  radiusSlider.addEventListener("change", () => {
    if (currentUserLocation) {
      searchCourtsByLocation(
        currentUserLocation.latitude,
        currentUserLocation.longitude,
        radiusSlider.value
      );
    }
  });
}

// Fetch all courts from the API
async function fetchCourts() {
  const courtsContainer = document.getElementById("courts-container");

  try {
    const response = await fetch(`${API_BASE_URL}/courts`);

    if (!response.ok) {
      throw new Error("Failed to fetch courts");
    }

    const data = await response.json();

    if (!data.courts || data.courts.length === 0) {
      courtsContainer.innerHTML = `
        <div class="col-12 text-center">
          <p>No courts available yet.</p>
        </div>
      `;
      return;
    }

    courtsContainer.innerHTML = "";

    data.courts.forEach((court) => {
      const courtCard = document.createElement("div");
      courtCard.className = "col-md-6 col-lg-4 mb-4";
      courtCard.innerHTML = `
        <div class="card court-card">
          <div class="card-body">
            <h5 class="card-title">${court.name}</h5>
            <p class="card-text">${court.address || "No address provided"}</p>
            <button class="btn btn-primary" onclick="navigateTo('court-details', ${
              court.court_id
            })">View Details</button>
          </div>
        </div>
      `;
      courtsContainer.appendChild(courtCard);
    });
  } catch (error) {
    console.error("Error fetching courts:", error);
    courtsContainer.innerHTML = `
      <div class="col-12">
        <div class="alert alert-danger">
          Failed to load courts: ${error.message}
        </div>
      </div>
    `;
  }
}

// Search courts function
async function searchCourts(query) {
  if (!query) {
    loadCourtsPage();
    return;
  }

  const courtsContainer = document.getElementById("courts-container");
  courtsContainer.innerHTML = `
    <div class="col-12 text-center">
        <div class="spinner-border" role="status">
            <span class="visually-hidden">Searching...</span>
        </div>
    </div>
  `;

  try {
    const response = await fetch(
      `${API_BASE_URL}/search/courts?q=${encodeURIComponent(query)}`
    );
    if (!response.ok) {
      throw new Error("Search failed");
    }

    const data = await response.json();

    if (!data.courts || data.courts.length === 0) {
      courtsContainer.innerHTML = `
        <div class="col-12 text-center">
            <p>No courts found matching "${query}".</p>
            <button class="btn btn-primary" onclick="loadCourtsPage()">Show All Courts</button>
        </div>
      `;
      return;
    }

    courtsContainer.innerHTML = "";

    data.courts.forEach((court) => {
      const courtCard = document.createElement("div");
      courtCard.className = "col-md-6 col-lg-4 mb-4";
      courtCard.innerHTML = `
        <div class="card court-card">
            <div class="card-body">
                <h5 class="card-title">${court.name}</h5>
                <p class="card-text">${
                  court.address || "No address provided"
                }</p>
                <button class="btn btn-primary" onclick="navigateTo('court-details', ${
                  court.court_id
                })">View Details</button>
            </div>
        </div>
      `;
      courtsContainer.appendChild(courtCard);
    });

    // Show search method information
    const searchMethodInfo = document.createElement("div");
    searchMethodInfo.className = "col-12 mt-3";
    searchMethodInfo.innerHTML = `
      <div class="alert alert-info">
          Search method: ${data.search_method} | Found ${data.courts.length} results for "${query}"
          <button class="btn btn-sm btn-primary float-end" onclick="loadCourtsPage()">Show All Courts</button>
      </div>
    `;
    courtsContainer.appendChild(searchMethodInfo);
  } catch (error) {
    console.error("Error searching courts:", error);
    courtsContainer.innerHTML = `
      <div class="col-12">
          <div class="alert alert-danger">
              Search failed. Please try again.
          </div>
          <button class="btn btn-primary" onclick="loadCourtsPage()">Show All Courts</button>
      </div>
    `;
  }
}

// Search courts by location
async function searchCourtsByLocation(lat, lng, radius = 10) {
  const courtsContainer = document.getElementById("courts-container");
  courtsContainer.innerHTML = `
    <div class="col-12 text-center">
        <div class="spinner-border" role="status">
            <span class="visually-hidden">Searching...</span>
        </div>
    </div>
  `;

  try {
    const response = await fetch(
      `${API_BASE_URL}/search/courts?lat=${lat}&lng=${lng}&radius=${radius}`
    );

    if (!response.ok) {
      throw new Error("Location search failed");
    }

    const data = await response.json();

    if (!data.courts || data.courts.length === 0) {
      courtsContainer.innerHTML = `
        <div class="col-12 text-center">
            <p>No courts found within ${radius} km of your location.</p>
            <button class="btn btn-primary" onclick="loadCourtsPage()">Show All Courts</button>
        </div>
      `;
      return;
    }

    courtsContainer.innerHTML = `
      <div class="col-12 mb-3">
        <div class="alert alert-info">
          Showing ${data.courts.length} courts within ${radius} km of your location
        </div>
      </div>
    `;

    data.courts.forEach((court) => {
      const courtCard = document.createElement("div");
      courtCard.className = "col-md-6 col-lg-4 mb-4";
      courtCard.innerHTML = `
        <div class="card court-card">
            <div class="card-body">
                <h5 class="card-title">${court.name}</h5>
                <p class="card-text">${
                  court.address || "No address provided"
                }</p>
                <p class="card-text text-success">
                  <strong>${court.distance} km away</strong>
                </p>
                <button class="btn btn-primary" onclick="navigateTo('court-details', ${
                  court.court_id
                })">View Details</button>
            </div>
        </div>
      `;
      courtsContainer.appendChild(courtCard);
    });
  } catch (error) {
    console.error("Error searching courts by location:", error);
    courtsContainer.innerHTML = `
      <div class="col-12 text-center">
          <p class="text-danger">Error searching for courts: ${error.message}</p>
          <button class="btn btn-primary" onclick="loadCourtsPage()">Show All Courts</button>
      </div>
    `;
  }
}

// Additional functions for courts, scheduling games, etc. would be implemented here

// Add an alias for loadScheduleGamePage to fix any references to it
function loadScheduleGamePage(courtId = null) {
  console.log(
    "loadScheduleGamePage alias called, redirecting to loadScheduleGameForm"
  );
  return loadScheduleGameForm(courtId);
}
