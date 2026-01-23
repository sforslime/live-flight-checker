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
        document.getElementById('results-separator').classList.add('hidden'); // Hide line
        errorMsg.classList.add('hidden');
        loading.classList.remove('hidden');
        searchBtnText.textContent = 'Searching...';
        searchBtnIcon.classList.add('animate-spin');
        searchBtnIcon.textContent = 'refresh'; // Switch arrow to spinner or use animate-spin on 'sync'

        const formData = new FormData(searchForm);
        const origin = formData.get('origin').toUpperCase().trim();
        const destination = formData.get('destination').toUpperCase().trim();
        const date = formData.get('date');

        // Construct URL
        const params = new URLSearchParams({
            origin,
            destination,
            date
        });

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

            document.getElementById('results-separator').classList.remove('hidden');
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

    const cityMap = {
        "LOS": "Lagos",
        "ABV": "Abuja",
        "PHC": "Port Harcourt",
        "KAN": "Kano",
        "ENU": "Enugu",
        "QW": "Owerri",
        "BNI": "Benin",
        "IBA": "Ibadan",
        "ILR": "Ilorin",
        "GMO": "Gombe"
    };

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
            // Card Container
            card.className = 'flight-card bg-surface-light dark:bg-surface-dark p-6 rounded-2xl shadow-soft dark:shadow-none border border-gray-100 dark:border-gray-700 w-full hover:shadow-lg transition-all duration-300';

            const deptDate = new Date(flight.departure_time);
            const arrDate = new Date(flight.arrival_time);

            const deptTime = deptDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
            const arrTime = arrDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });

            // Duration Calc
            const diffMs = arrDate - deptDate;
            const diffHrs = Math.floor(diffMs / 3600000);
            const diffMins = Math.round(((diffMs % 3600000) / 60000));
            const durationStr = `${diffHrs}h ${diffMins}m`;

            const formatter = new Intl.NumberFormat('en-NG', {
                style: 'currency',
                currency: flight.currency || 'NGN',
                maximumFractionDigits: 0
            });

            const originCity = cityMap[flight.origin] || flight.origin;
            const destCity = cityMap[flight.destination] || flight.destination;
            const airlineInitial = flight.airline.charAt(0);

            // Generate Airline Logo
            let logoContent;
            let logoBg;

            if (flight.airline === "ValueJet") {
                logoContent = `<img src="/static/images/valuejet.png" alt="ValueJet" class="w-full h-full object-contain p-2">`;
                logoBg = "bg-white border border-gray-100";
            } else if (flight.airline === "XEJet") {
                logoContent = `<img src="/static/images/xejet.png" alt="XEJet" class="w-full h-full object-contain p-2">`;
                logoBg = "bg-white border border-gray-100";
            } else if (flight.airline === "Air Peace") {
                logoContent = `<img src="/static/images/airpeace.png" alt="Air Peace" class="w-full h-full object-contain p-1">`;
                logoBg = "bg-white border border-gray-100";
            } else {
                // Keep random pastel fallback for others
                const colors = ['bg-emerald-200', 'bg-blue-200', 'bg-purple-200', 'bg-orange-200', 'bg-rose-200'];
                const colorIdx = flight.airline.length % colors.length;
                logoBg = colors[colorIdx];
                logoContent = flight.airline.charAt(0);
            }

            card.innerHTML = `
                <div class="flex flex-col md:flex-row items-center justify-between gap-6">
                    
                    <!-- Left: Airline Logo & Info -->
                    <div class="flex items-center gap-4 w-full md:w-auto">
                        <div class="h-14 w-14 rounded-full ${logoBg} flex items-center justify-center text-gray-700 font-bold text-xl shadow-sm overflow-hidden">
                            ${logoContent}
                        </div>
                    </div>

                    <!-- Middle: Flight Details -->
                    <div class="flex flex-1 items-center justify-between w-full md:w-auto px-2 md:px-12 gap-4">
                        
                        <!-- Departure -->
                        <div class="text-left">
                            <div class="text-3xl font-bold text-text-light dark:text-text-dark">${deptTime}</div>
                            <div class="text-sm text-subtext-light dark:text-subtext-dark font-medium">${flight.origin} • ${originCity}</div>
                        </div>

                        <!-- Duration / Nonstop -->
                        <div class="flex flex-col items-center justify-center w-full px-4">
                            <span class="text-xs text-subtext-light dark:text-subtext-dark mb-1">${durationStr}</span>
                            <div class="flex items-center w-full gap-2">
                                <div class="h-[1px] bg-gray-300 dark:bg-gray-600 w-full"></div>
                                <span class="text-[10px] font-bold text-subtext-light dark:text-subtext-dark uppercase tracking-wider whitespace-nowrap">NONSTOP</span>
                                <div class="h-[1px] bg-gray-300 dark:bg-gray-600 w-full"></div>
                            </div>
                        </div>

                        <!-- Arrival -->
                        <div class="text-right">
                            <div class="text-3xl font-bold text-text-light dark:text-text-dark">${arrTime}</div>
                            <div class="text-sm text-subtext-light dark:text-subtext-dark font-medium">${flight.destination} • ${destCity}</div>
                        </div>
                    </div>

                    <!-- Divider (Desktop only) -->
                    <div class="hidden md:block w-[1px] h-16 bg-gray-200 dark:bg-gray-700 mx-2"></div>

                    <!-- Right: Price & Action -->
                    <div class="text-right flex flex-row md:flex-col items-center md:items-end justify-between w-full md:w-auto mt-4 md:mt-0 gap-4">
                        <div class="text-right">
                            <div class="text-3xl font-bold text-text-light dark:text-text-dark">${formatter.format(flight.price)}</div>
                            <div class="text-xs text-subtext-light dark:text-subtext-dark">One way</div>
                        </div>
                        
                        <a href="${flight.booking_link || '#'}" target="_blank" 
                           class="bg-[#4285F4] hover:bg-blue-600 text-white font-medium py-2 px-8 rounded-full transition-colors shadow-sm text-sm">
                           ${flight.booking_link ? 'Select' : 'View'}
                        </a>
                    </div>
                </div>
            `;

            resultsArea.appendChild(card);
        });
    }
});
