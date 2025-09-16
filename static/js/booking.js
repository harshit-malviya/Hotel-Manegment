// Booking Form JavaScript

// Global variables
let reservationSources = [];
let selectedSourceId = null;

// Auto-calculate total amount when dates or room changes
function initializeAmountCalculation() {
    console.log('Initializing amount calculation...');
    
    const checkInDate = document.querySelector('#id_check_in_date');
    const checkOutDate = document.querySelector('#id_check_out_date');
    const roomSelect = document.querySelector('#id_room');
    const ratePlanSelect = document.querySelector('#id_rate_plan');
    const totalAmountField = document.querySelector('#id_total_amount');
    const adultsField = document.querySelector('#id_number_of_adults');
    const childrenField = document.querySelector('#id_number_of_children');
    
    console.log('Form elements found:', {
        checkInDate: !!checkInDate,
        checkOutDate: !!checkOutDate,
        roomSelect: !!roomSelect,
        totalAmountField: !!totalAmountField
    });
    
    // Make calculateTotal globally accessible
    window.calculateTotalAmount = function calculateTotal() {
        console.log('calculateTotalAmount called'); // Debug log
        
        if (!checkInDate || !checkOutDate || !roomSelect || !totalAmountField) {
            console.log('Missing required fields for calculation');
            return;
        }
        
        if (checkInDate.value && checkOutDate.value && roomSelect.value) {
            console.log('All required values present, calculating...'); // Debug log
            
            const checkIn = new Date(checkInDate.value);
            const checkOut = new Date(checkOutDate.value);
            const nights = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
            
            if (nights > 0) {
                // Show calculating indicator
                totalAmountField.value = 'Calculating...';
                totalAmountField.style.backgroundColor = '#fff3cd';
                
                // Make AJAX call to get calculated amount
                const formData = new FormData();
                formData.append('check_in_date', checkInDate.value);
                formData.append('check_out_date', checkOutDate.value);
                formData.append('room', roomSelect.value);
                formData.append('rate_plan', ratePlanSelect ? ratePlanSelect.value || '' : '');
                formData.append('number_of_adults', adultsField ? adultsField.value || '1' : '1');
                formData.append('number_of_children', childrenField ? childrenField.value || '0' : '0');
                formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
                
                console.log('Sending calculation request...'); // Debug log
                
                fetch('/bookings/calculate-amount/', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    console.log('Response received:', response.status); // Debug log
                    return response.json();
                })
                .then(data => {
                    console.log('Calculation data:', data); // Debug log
                    
                    if (data.total_amount) {
                        totalAmountField.value = data.total_amount;
                        totalAmountField.style.backgroundColor = '#d4edda';
                        
                        // Show calculation details
                        let helpText = totalAmountField.parentNode.querySelector('.calculation-help');
                        if (!helpText) {
                            helpText = document.createElement('small');
                            helpText.className = 'form-help calculation-help';
                            totalAmountField.parentNode.appendChild(helpText);
                        }
                        helpText.textContent = `${nights} nights × ₹${data.rate_per_night} = ₹${data.total_amount}`;
                        helpText.style.color = '#28a745';
                        helpText.style.fontWeight = '500';
                    } else if (data.error) {
                        console.error('Calculation error:', data.error);
                        totalAmountField.value = '';
                        totalAmountField.style.backgroundColor = '#f8d7da';
                        totalAmountField.placeholder = 'Error calculating amount';
                    }
                })
                .catch(error => {
                    console.error('Error calculating amount:', error);
                    totalAmountField.value = '';
                    totalAmountField.style.backgroundColor = '#f8d7da';
                    totalAmountField.placeholder = 'Error calculating amount';
                });
            } else {
                console.log('Invalid date range, nights:', nights);
                totalAmountField.value = '';
                totalAmountField.placeholder = 'Invalid date range';
            }
        } else {
            console.log('Missing values - CheckIn:', checkInDate.value, 'CheckOut:', checkOutDate.value, 'Room:', roomSelect.value);
            totalAmountField.value = '';
            totalAmountField.placeholder = 'Select dates and room';
        }
    }
    
    // Add event listeners
    [checkInDate, checkOutDate, roomSelect, ratePlanSelect, adultsField, childrenField].forEach(field => {
        if (field) {
            field.addEventListener('change', window.calculateTotalAmount);
        }
    });
    
    // Calculate on page load if editing
    if (checkInDate && checkOutDate && roomSelect && checkInDate.value && checkOutDate.value && roomSelect.value) {
        window.calculateTotalAmount();
    }
}

// Reservation Source Search Functionality
function initializeReservationSourceSearch() {
    const bookingSourceSelect = document.querySelector('#id_booking_source');
    const reservationSourceInput = document.querySelector('#id_reservation_source');
    const reservationSourceDropdown = document.querySelector('#reservationSourceDropdown');
    const reservationSourceIdInput = document.querySelector('#id_reservation_source_id');
    
    if (!reservationSourceInput) return;
    
    // Fetch reservation sources from server
    async function fetchReservationSources() {
        try {
            const response = await fetch('/bookings/api/reservation-sources/');
            if (response.ok) {
                reservationSources = await response.json();
            }
        } catch (error) {
            console.error('Error fetching reservation sources:', error);
        }
    }
    
    // Filter and display reservation sources
    function filterReservationSources(searchTerm = '') {
        const selectedBookingSource = bookingSourceSelect.value;
        
        // Hide dropdown if booking source is DIRECT
        const reservationSourceDiv = reservationSourceInput.closest('div');
        if (selectedBookingSource === 'DIRECT') {
            reservationSourceDiv.style.display = 'none';
            reservationSourceDropdown.style.display = 'none';
            return;
        } else {
            reservationSourceDiv.style.display = 'block';
        }
        
        // Filter sources based on search term and booking source
        const filteredSources = reservationSources.filter(source => {
            const matchesSearch = searchTerm === '' || 
                source.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                source.source_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (source.contact_person && source.contact_person.toLowerCase().includes(searchTerm.toLowerCase()));
            
            return matchesSearch && source.is_active;
        });
        
        // Display filtered results
        if (searchTerm && filteredSources.length > 0) {
            reservationSourceDropdown.innerHTML = filteredSources.map(source => `
                <div class="reservation-source-item" data-id="${source.id}" data-name="${source.name}">
                    <div style="font-weight: bold;">${source.name}</div>
                    <div style="font-size: 12px; color: #666;">
                        ${source.source_id} • ${source.source_type_display}
                        ${source.contact_person ? ' • ' + source.contact_person : ''}
                    </div>
                </div>
            `).join('');
            reservationSourceDropdown.style.display = 'block';
        } else if (searchTerm) {
            reservationSourceDropdown.innerHTML = `
                <div style="padding: 10px; color: #666; text-align: center;">
                    No reservation sources found matching "${searchTerm}"
                </div>
            `;
            reservationSourceDropdown.style.display = 'block';
        } else {
            reservationSourceDropdown.style.display = 'none';
        }
    }
    
    // Handle reservation source input
    reservationSourceInput.addEventListener('input', function() {
        const searchTerm = this.value;
        filterReservationSources(searchTerm);
        
        // Clear selection if input is cleared
        if (!searchTerm) {
            selectedSourceId = null;
            reservationSourceIdInput.value = '';
        }
    });
    
    reservationSourceInput.addEventListener('focus', function() {
        if (this.value) {
            filterReservationSources(this.value);
        }
    });
    
    // Handle clicking outside to close dropdown
    document.addEventListener('click', function(event) {
        if (!reservationSourceInput.contains(event.target) && 
            !reservationSourceDropdown.contains(event.target)) {
            reservationSourceDropdown.style.display = 'none';
        }
    });
    
    // Handle clicking on reservation source items
    reservationSourceDropdown.addEventListener('click', function(event) {
        const item = event.target.closest('.reservation-source-item');
        if (item) {
            const sourceId = item.dataset.id;
            const sourceName = item.dataset.name;
            
            reservationSourceInput.value = sourceName;
            reservationSourceIdInput.value = sourceId;
            selectedSourceId = sourceId;
            reservationSourceDropdown.style.display = 'none';
        }
    });
    
    // Handle booking source changes
    if (bookingSourceSelect) {
        bookingSourceSelect.addEventListener('change', function() {
            // Clear reservation source when booking source changes
            reservationSourceInput.value = '';
            reservationSourceIdInput.value = '';
            selectedSourceId = null;
            filterReservationSources();
        });
    }
    
    // Initialize
    fetchReservationSources().then(() => {
        if (bookingSourceSelect) {
            filterReservationSources();
        }
        
        // Pre-populate reservation source if editing
        const existingSourceId = reservationSourceIdInput.value;
        if (existingSourceId && reservationSources.length > 0) {
            const existingSource = reservationSources.find(s => s.id == existingSourceId);
            if (existingSource) {
                reservationSourceInput.value = existingSource.name;
                selectedSourceId = existingSourceId;
            }
        }
    });
}

// Room Type Selection Functionality
function initializeRoomTypeSelection() {
    const roomTypeSelect = document.querySelector('#id_room_type');
    const roomSelect = document.querySelector('#id_room');
    const checkInDate = document.querySelector('#id_check_in_date');
    const checkOutDate = document.querySelector('#id_check_out_date');
    const loadingIndicator = document.querySelector('#room-loading');
    
    if (!roomTypeSelect || !roomSelect) return;
    
    // Function to load available rooms based on room type
    async function loadAvailableRooms() {
        const roomTypeId = roomTypeSelect.value;
        const checkIn = checkInDate ? checkInDate.value : '';
        const checkOut = checkOutDate ? checkOutDate.value : '';
        const bookingId = document.querySelector('input[name="booking_id"]') ? 
                         document.querySelector('input[name="booking_id"]').value : '';
        
        if (!roomTypeId) {
            roomSelect.innerHTML = '<option value="">First select a room type</option>';
            roomSelect.disabled = true;
            return;
        }
        
        // Show loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }
        roomSelect.disabled = true;
        roomSelect.innerHTML = '<option value="">Loading rooms...</option>';
        
        try {
            const params = new URLSearchParams({
                room_type_id: roomTypeId,
                check_in_date: checkIn,
                check_out_date: checkOut,
                booking_id: bookingId
            });
            
            const response = await fetch(`/bookings/api/rooms-by-type/?${params}`);
            const data = await response.json();
            
            if (response.ok && data.rooms) {
                // Clear existing options
                roomSelect.innerHTML = '<option value="">Select a room</option>';
                
                // Add available rooms
                data.rooms.forEach(room => {
                    const option = document.createElement('option');
                    option.value = room.id;
                    option.textContent = room.display_name;
                    option.dataset.rate = room.rate;
                    option.dataset.capacity = room.max_occupancy;
                    roomSelect.appendChild(option);
                });
                
                // Show room type info
                if (data.rooms.length > 0) {
                    const helpText = roomSelect.parentNode.querySelector('small') || 
                                   document.createElement('small');
                    helpText.className = 'form-help';
                    helpText.textContent = `${data.rooms.length} rooms available • ₹${data.room_type_price}/night • Capacity: ${data.room_type_capacity} guests`;
                    helpText.style.color = '#28a745';
                    
                    if (!roomSelect.parentNode.querySelector('small')) {
                        roomSelect.parentNode.appendChild(helpText);
                    }
                } else {
                    roomSelect.innerHTML = '<option value="">No rooms available for selected dates</option>';
                }
                
                roomSelect.disabled = false;
                
                // Re-attach event listener for amount calculation
                // Remove existing listener first to avoid duplicates
                roomSelect.removeEventListener('change', window.calculateTotalAmount);
                roomSelect.addEventListener('change', window.calculateTotalAmount);
            } else {
                roomSelect.innerHTML = '<option value="">Error loading rooms</option>';
                console.error('Error loading rooms:', data.error || 'Unknown error');
            }
        } catch (error) {
            roomSelect.innerHTML = '<option value="">Error loading rooms</option>';
            console.error('Error loading rooms:', error);
        } finally {
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        }
    }
    
    // Event listeners
    roomTypeSelect.addEventListener('change', function() {
        loadAvailableRooms();
        // Clear total amount when room type changes since room will change
        const totalAmountField = document.querySelector('#id_total_amount');
        if (totalAmountField) {
            totalAmountField.value = '';
            totalAmountField.style.backgroundColor = '';
            totalAmountField.placeholder = 'Select a room to calculate';
        }
    });
    
    // Also reload rooms when dates change
    if (checkInDate) {
        checkInDate.addEventListener('change', () => {
            if (roomTypeSelect.value) {
                loadAvailableRooms();
            }
            // Trigger amount calculation if room is already selected
            setTimeout(() => {
                if (window.calculateTotalAmount && roomSelect.value) {
                    window.calculateTotalAmount();
                }
            }, 500); // Small delay to allow room loading to complete
        });
    }
    
    if (checkOutDate) {
        checkOutDate.addEventListener('change', () => {
            if (roomTypeSelect.value) {
                loadAvailableRooms();
            }
            // Trigger amount calculation if room is already selected
            setTimeout(() => {
                if (window.calculateTotalAmount && roomSelect.value) {
                    window.calculateTotalAmount();
                }
            }, 500); // Small delay to allow room loading to complete
        });
    }
    
    // Load rooms on page load if room type is already selected (for editing)
    if (roomTypeSelect.value) {
        loadAvailableRooms();
    }
}

// Initialize calculate button
function initializeCalculateButton() {
    const calculateBtn = document.querySelector('#calculate-amount-btn');
    if (calculateBtn) {
        calculateBtn.addEventListener('click', function() {
            console.log('Calculate button clicked');
            if (window.calculateTotalAmount) {
                window.calculateTotalAmount();
            }
        });
    }
}

// Debug function for testing from browser console
window.debugBookingForm = function() {
    console.log('=== Booking Form Debug Info ===');
    
    const elements = {
        checkInDate: document.querySelector('#id_check_in_date'),
        checkOutDate: document.querySelector('#id_check_out_date'),
        roomType: document.querySelector('#id_room_type'),
        room: document.querySelector('#id_room'),
        totalAmount: document.querySelector('#id_total_amount'),
        calculateBtn: document.querySelector('#calculate-amount-btn')
    };
    
    console.log('Form elements:', elements);
    
    Object.keys(elements).forEach(key => {
        const element = elements[key];
        if (element) {
            console.log(`${key}:`, {
                value: element.value,
                disabled: element.disabled,
                visible: element.offsetParent !== null
            });
        } else {
            console.log(`${key}: NOT FOUND`);
        }
    });
    
    console.log('calculateTotalAmount function available:', typeof window.calculateTotalAmount);
    
    // Test calculation if possible
    if (elements.checkInDate?.value && elements.checkOutDate?.value && elements.room?.value) {
        console.log('Testing calculation...');
        window.calculateTotalAmount();
    } else {
        console.log('Cannot test calculation - missing required values');
    }
};

// Initialize all booking form functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - initializing booking form...');
    
    // Initialize with a small delay to ensure all elements are rendered
    setTimeout(() => {
        initializeAmountCalculation();
        initializeReservationSourceSearch();
        initializeRoomTypeSelection();
        initializeCalculateButton();
        
        console.log('Booking form initialization complete');
        console.log('Use debugBookingForm() in console to debug');
    }, 100);
});