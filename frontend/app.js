document.addEventListener('DOMContentLoaded', () => {
    // Initialize Custom Date Picker
    const dateInput = document.getElementById('date');
    const fp = flatpickr(dateInput, {
        minDate: "today",
        defaultDate: new Date().fp_incr(1), // Tomorrow
        dateFormat: "Y-m-d",
        disableMobile: true, // Boolean true prevents native picker on mobile
        theme: "light",
        allowInput: true // Allow typing if needed, but picker guides it
    });

    // Make the purple button toggle the calendar
    const calendarBtn = document.getElementById('calendar-btn');
    if (calendarBtn) {
        calendarBtn.addEventListener('click', () => {
            fp.open();
        });
    }

    // State management
    let selectedAirlines = new Set(["ALL"]);
    let currentSort = "cheapest";
    let currentFlights = []; // Store fetched flights for client-side sorting

    // Airline Filter Logic
    const airlineSelect = document.getElementById('airline-filter');
    const airlineLabel = document.getElementById('airline-filter-label');

    airlineSelect.addEventListener('change', (e) => {
        const val = e.target.value;

        if (val === "ALL") {
            selectedAirlines.clear();
            selectedAirlines.add("ALL");
        } else {
            if (selectedAirlines.has("ALL")) {
                selectedAirlines.delete("ALL");
            }

            if (selectedAirlines.has(val)) {
                selectedAirlines.delete(val);
            } else {
                selectedAirlines.add(val);
            }

            if (selectedAirlines.size === 0) {
                selectedAirlines.add("ALL");
            }
        }

        updateAirlineLabel();

        // Reset select to allow re-selection (toggle behavior)
        // We temporarily disable the listener or just accept that "ALL" might be re-triggered
        airlineSelect.value = "ALL";
    });

    function updateAirlineLabel() {
        if (selectedAirlines.has("ALL")) {
            airlineLabel.textContent = "All Airlines";
            airlineLabel.classList.remove('text-primary');
        } else {
            const arr = Array.from(selectedAirlines);
            if (arr.length === 1) {
                airlineLabel.textContent = arr[0];
            } else {
                airlineLabel.textContent = `${arr[0]} + ${arr.length - 1}`;
            }
            airlineLabel.classList.add('text-primary');
        }
    }

    // Sort Filter Logic
    const sortSelect = document.getElementById('sort-filter');
    const sortLabel = document.getElementById('sort-filter-label');

    sortSelect.addEventListener('change', (e) => {
        currentSort = e.target.value;
        const text = e.target.options[e.target.selectedIndex].text;
        sortLabel.textContent = `Sort by: ${text.replace('Departure', '')}`;

        // Re-sort existing results
        if (currentFlights.length > 0) {
            renderResults(currentFlights);
        }
    });

    const searchForm = document.getElementById('search-form');

    const resultsArea = document.getElementById('results-area');
    const loading = document.getElementById('loading');
    const errorMsg = document.getElementById('error-message');
    const searchBtnText = document.querySelector('#search-btn span:first-child');
    const searchBtnIcon = document.querySelector('#search-btn span:last-child');

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI State: Loading
        resultsArea.innerHTML = ''; // Clear results
        errorMsg.classList.add('hidden');
        loading.classList.remove('hidden');
        searchBtnText.textContent = 'Searching...';
        searchBtnIcon.classList.add('animate-spin');
        searchBtnIcon.textContent = 'refresh'; // Switch arrow to spinner or use animate-spin on 'sync'

        const formData = new FormData(searchForm);
        const origin = formData.get('origin').toUpperCase().trim();
        const destination = formData.get('destination').toUpperCase().trim();
        const date = formData.get('date');

        // Construct URL with airlines
        const params = new URLSearchParams({
            origin,
            destination,
            date
        });

        if (!selectedAirlines.has("ALL")) {
            selectedAirlines.forEach(a => params.append('airlines', a));
        }

        try {
            const response = await fetch(`/api/search?${params.toString()}`);
            const data = await response.json();

            loading.classList.add('hidden');
            searchBtnText.textContent = 'Search Flights';
            searchBtnIcon.classList.remove('animate-spin');
            searchBtnIcon.textContent = 'arrow_forward';

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to fetch flights');
            }

            if (data.length === 0) {
                errorMsg.textContent = "No flights found for this route and date.";
                errorMsg.classList.remove('hidden');
                currentFlights = [];
                return;
            }

            currentFlights = data;
            renderResults(data);

        } catch (error) {
            loading.classList.add('hidden');
            searchBtnText.textContent = 'Search Flights';
            searchBtnIcon.classList.remove('animate-spin');
            searchBtnIcon.textContent = 'arrow_forward';

            errorMsg.textContent = error.message;
            errorMsg.classList.remove('hidden');
            currentFlights = [];
        }
    });

    function renderResults(flights) {
        // Sort logic
        const sorted = [...flights]; // Copy
        if (currentSort === 'cheapest') {
            sorted.sort((a, b) => a.price - b.price);
        } else if (currentSort === 'highest') {
            sorted.sort((a, b) => b.price - a.price);
        } else if (currentSort === 'earliest') {
            sorted.sort((a, b) => new Date(a.departure_time) - new Date(b.departure_time));
        } else if (currentSort === 'latest') {
            sorted.sort((a, b) => new Date(b.departure_time) - new Date(a.departure_time));
        }

        resultsArea.innerHTML = '';

        sorted.forEach(flight => {
            const card = document.createElement('div');
            // Tailwind styling for the results card to match the "Surface" look
            card.className = 'flight-card flex flex-col md:flex-row justify-between items-center bg-surface-light dark:bg-surface-dark p-6 rounded-2xl shadow-soft border border-gray-100 dark:border-gray-700 w-full hover:shadow-lg transition-all duration-300';

            const deptTime = new Date(flight.departure_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const arrTime = new Date(flight.arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            const formatter = new Intl.NumberFormat('en-NG', {
                style: 'currency',
                currency: flight.currency || 'NGN'
            });

            // "Amadeus" vs "Scraper" badge
            const sourceBadgeColor = flight.source === 'Amadeus' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800';

            card.innerHTML = `
                <div class="flex-1 w-full md:w-auto mb-4 md:mb-0">
                    <div class="flex items-center gap-3 mb-2">
                        <span class="text-xl font-bold text-text-light dark:text-text-dark">${flight.airline}</span>
                        <span class="text-xs px-2 py-1 rounded-full ${sourceBadgeColor} font-medium">${flight.source}</span>
                    </div>
                    
                    <div class="flex items-center gap-6 text-subtext-light dark:text-subtext-dark">
                        <div class="flex flex-col">
                            <span class="text-2xl font-semibold text-text-light dark:text-text-dark">${deptTime}</span>
                            <span class="text-sm text-subtext-light">${flight.origin}</span>
                        </div>
                        <div class="flex flex-col items-center">
                            <span class="material-icons text-gray-300">flight_takeoff</span>
                            <span class="text-xs text-gray-400">Direct</span>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-2xl font-semibold text-text-light dark:text-text-dark">${arrTime}</span>
                            <span class="text-sm text-subtext-light">${flight.destination}</span>
                        </div>
                    </div>
                </div>

                <div class="flex flex-col items-end gap-2 w-full md:w-auto">
                    <span class="text-3xl font-bold text-primary">${formatter.format(flight.price)}</span>
                    <a href="${flight.booking_link || '#'}" target="_blank" 
                       class="px-6 py-2 bg-text-light dark:bg-text-dark text-surface-light dark:text-surface-dark rounded-full font-medium hover:opacity-90 transition-opacity">
                       ${flight.booking_link ? 'Book Now ↗' : 'View Details'}
                    </a>
                </div>
            `;

            resultsArea.appendChild(card);
        });
    }
});
