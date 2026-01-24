# Naija Flights - Live Flight Checker ✈️

A modern, hybrid flight search engine designed to find the cheapest realtime prices for domestic Nigerian flights. It seamlessly combines data from global GDS systems (via Amadeus API) with direct airline website scraping to provide complete market coverage.

<a href="#" title="Complete-ish. Fork and commit for more featuresss"><img src="https://img.shields.io/badge/status-complete-green"></a>
<a href="#-key-features" title="Yurrrr"><img src="https://img.shields.io/badge/python-3.10%2B-blue"></a>
<a href="#-contributions" title="Grace this project with your contributions!"><img src="https://img.shields.io/badge/contributions-welcome-purple.svg"></a>
<a href="https://twitter.com/sforslime" title="AYO! on Twitter"><img src="https://img.shields.io/twitter/follow/sforslime.svg?style=social&label=Follow"></a>

## 🌟 Key Features

*   **Hybrid Search Engine**: Queries both the Amadeus API (for major carriers like Air Peace) and direct airline websites (ValueJet, XEJet) in parallel for maximum speed.
*   **Smart Scrapers (Selenium)**:
    *   **ValueJet (React/Next.js)**: 
        *   Navigates a modern SPA which relies heavily on client-side hydration.
        *   Implements intelligent waiting strategies to ensure the DOM is fully interactive before scraping.
        *   Bypasses complex read-only UI components (like PrimeReact calendars) by directly injecting values into the application state via JavaScript execution.
    *   **XEJet (AeroCRS/ASP.NET)**:
        *   Handles legacy form submissions and `.aspx` postbacks.
        *   Automates interaction with jQuery UI datepickers by traversing the calendar DOM structure.
        *   Uses robust partial-text matching for dropdowns to handle inconsistent airport naming conventions across systems.
    *   **Resilience & Debugging**: 
        *   Built on a robust `BaseScraper` class that handles driver lifecycle and User-Agent rotation.
        *   Automatically captures and saves screenshots to `backend/screenshots/` whenever an error occurs, allowing for "time-travel" debugging of failed scraping attempts.
*   **Premium Web Interface**:
    *   **Gemini-Inspired Design**: Clean, glassmorphic UI with responsive TailwindCSS layout.
    *   **Interactive Results**: Filter by airline, sort by price/time, and view flight details with ease.
    *   **Visual Separators**: Subtle animations for a polished user experience.

## 🛠️ Technology Stack

*   **Backend**: Python, FastAPI, Selenium WebDriver (Chrome), Amadeus SDK.
*   **Frontend**: HTML5, Vanilla JavaScript (ES6+), TailwindCSS.
*   **Infrastructure**: `asyncio` for concurrency, `uvicorn` server.

## 🚀 Installation & Setup Guide

Follow these steps to run the project locally on your machine.

### 1. Prerequisites

Ensure you have the following installed:
*   **Python 3.10+**: [Download Here](https://www.python.org/downloads/)
*   **Google Chrome**: The web scrapers require a local installation of the Google Chrome browser to function.
*   **Git**: To clone the repository.

### 2. Clone the Repository

```bash
git clone https://github.com/sforslime/live-flight-checker.git
cd live-flight-checker
```

### 3. Environment Setup

It is highly recommended to use a virtual environment.

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configuration (.env)

Create a file named `.env` in the root directory. You will need API keys from the [Amadeus for Developers](https://developers.amadeus.com/) portal.

```ini
AMADEUS_CLIENT_ID=your_client_id_here
AMADEUS_CLIENT_SECRET=your_client_secret_here
```

### 6. Running the App

Start the development server:

```bash
# Make sure your virtual environment is active!
export PYTHONPATH=$PYTHONPATH:. 
uvicorn backend.main:app --reload
```

The application will be accessible at: **http://127.0.0.1:8000**

## 📂 Project Structure

```
live-flight-checker/
├── backend/
│   ├── main.py              # Application entry point & API routes
│   ├── models.py            # Pydantic data models
│   ├── utils.py             # Helper utilities
│   ├── services/
│   │   ├── amadeus_client.py   # API integration logic
│   │   └── scrapers/           # Selenium scrapers
│   │       ├── base_scraper.py # Base class with common logic
│   │       ├── valuejet.py     # ValueJet implementation
│   │       └── xejet.py        # XEJet implementation
│   └── screenshots/         # Auto-generated debug screenshots (on error)
├── frontend/
│   ├── index.html           # Main HTML template
│   ├── app.js               # Frontend application logic
│   ├── style.css            # Custom CSS styles
│   └── images/              # Static assets (logos, favicon)
├── requirements.txt         # Dependency list
└── README.md                # Documentation
```

## 🔧 Troubleshooting

*   **Scraper Errors**: If scrapers fail immediately, ensure you have Google Chrome installed. The `webdriver-manager` package will automatically download the matching ChromeDriver, but the browser itself must be present.
*   **Screenshots**: If a scraper encounters an error, check the `backend/screenshots/` folder. It will contain a screenshot of the browser state at the moment of failure, helping you debug the issue.
*   **Amadeus Errors**: Ensure your API keys in `.env` are correct and that your developer account has available quota.

## 🙏 Contributions

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the project
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details. 
