# Naija Flights - Live Flight Checker ✈️

A modern, hybrid flight search engine designed to find the cheapest realtime prices for domestic Nigerian flights. It seamlessly combines data from global GDS systems (via Amadeus API) with direct airline website scraping to provide comprehensive coverage.

![Project Status](https://img.shields.io/badge/status-in%20development-orange)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)

## 🌟 Features

-   **Hybrid Search Engine**:
    -   **Amadeus API Integration**: Fetches standardized data for major carriers like Air Peace.
    -   *(Coming Soon)* **Custom Web Scrapers**: Specialized scrapers for airlines not on GDS (e.g., Ibom Air, ValueJet).
-   **Premium UI**:
    -   Gemini-inspired "TravelAI" design.
    -   Glassmorphism effects and smooth animations.
    -   Responsive layout with Dark Mode support (system preference).
    -   Custom-themed Date Picker (Flatpickr).
-   **FastAPI Backend**: High-performance, asynchronous Python backend.

## 🛠️ Tech Stack

-   **Backend**: Python, FastAPI, Uvicorn, Amadeus SDK.
-   **Frontend**: HTML5, TailwindCSS, Vanilla JavaScript.
-   **Tools**: Flatpickr (Calendar), Google Fonts (Outfit).

## 🚀 Getting Started

### Prerequisites

-   Python 3.10 or higher.
-   An Amadeus for Developers account (for API keys).

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/live-flight-checker.git
    cd live-flight-checker
    ```

2.  **Create a Virtual Environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the root directory and add your keys:
    ```ini
    AMADEUS_CLIENT_ID=your_client_id_here
    AMADEUS_CLIENT_SECRET=your_client_secret_here
    ```

### ▶️ Running the Application

1.  **Start the Server**
    ```bash
    uvicorn backend.main:app --reload
    ```

2.  **Open the App**
    Visit `http://127.0.0.1:8000` in your browser.

3.  **Usage**
    -   Select Origin (e.g., Lagos - LOS).
    -   Select Destination (e.g., Abuja - ABV).
    -   Pick a date using the custom calendar.
    -   Click "Search Flights" to see live results!

## 📂 Project Structure

```
live-flight-checker/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── models.py            # Data models (Pydantic)
│   ├── utils.py             # Helper functions (Airline codes)
│   └── services/
│       └── amadeus_client.py # Amadeus API logic
├── frontend/
│   ├── index.html           # Main UI
│   ├── style.css            # Custom animations & overrides
│   └── app.js               # Frontend logic
├── scripts/                 # Utility scripts (testing/verification)
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## ⚠️ Notes for Developers

-   **Security**: Never commit your `.env` file. It is already added to `.gitignore`.
-   **API Limits**: The Amadeus Self-Service API has rate limits. Check your quota if searches fail.

## 📜 License

This project is for educational purposes. 
