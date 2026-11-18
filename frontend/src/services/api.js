const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

function getAuthHeaders() {
  const token = localStorage.getItem('wanderwise_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
}

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    ...getAuthHeaders(),
    ...(options.headers || {})
  };

  try {
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // Auth
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  signup: (data) => request('/auth/signup', { method: 'POST', body: JSON.stringify(data) }),
  getProfile: () => request('/auth/me'),
  updatePreferences: (data) => request('/auth/preferences', { method: 'PUT', body: JSON.stringify(data) }),

  // Destinations
  getDestinations: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/destinations${query ? `?${query}` : ''}`);
  },
  recommendDestinations: (data) => request('/destinations/recommend', { method: 'POST', body: JSON.stringify(data) }),
  getSurpriseMe: () => request('/destinations/surprise-me'),
  getHiddenGems: () => request('/destinations/hidden-gems'),
  getMoodPlan: (data) => request('/destinations/mood-plan', { method: 'POST', body: JSON.stringify(data) }),

  // Trips
  getTrips: (status) => request(`/trips${status ? `?status=${status}` : ''}`),
  getTripDetail: (id) => request(`/trips/${id}`),
  createTrip: (data) => request('/trips', { method: 'POST', body: JSON.stringify(data) }),
  updateTrip: (id, data) => request(`/trips/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTrip: (id) => request(`/trips/${id}`, { method: 'DELETE' }),
  duplicateTrip: (id) => request(`/trips/${id}/duplicate`, { method: 'POST' }),

  // Itinerary & Activities
  addActivity: (tripId, dayId, data) => request(`/trips/${tripId}/days/${dayId}/activities`, { method: 'POST', body: JSON.stringify(data) }),
  updateActivity: (activityId, data) => request(`/trips/activities/${activityId}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteActivity: (activityId) => request(`/trips/activities/${activityId}`, { method: 'DELETE' }),

  // Weather & Routing
  getWeather: (lat, lng, days = 5) => request(`/weather?lat=${lat}&lng=${lng}&days=${days}`),
  getRoute: (origLat, origLng, destLat, destLng, mode = 'driving') => 
    request(`/weather/route?origin_lat=${origLat}&origin_lng=${origLng}&dest_lat=${destLat}&dest_lng=${destLng}&mode=${mode}`),
  replanForWeather: (tripId, dayNumber, condition = 'Rain') => 
    request('/weather/replan-day', { method: 'POST', body: JSON.stringify({ trip_id: tripId, day_number: dayNumber, current_weather_condition: condition }) }),

  // Budget
  getBudgetSummary: (tripId) => request(`/budget/${tripId}/summary`),
  getExpenses: (tripId) => request(`/budget/${tripId}/expenses`),
  addExpense: (tripId, data) => request(`/budget/${tripId}/expenses`, { method: 'POST', body: JSON.stringify(data) }),
  deleteExpense: (id) => request(`/budget/expenses/${id}`, { method: 'DELETE' }),

  // Group
  inviteGroupMember: (tripId, data) => request(`/group/${tripId}/invite`, { method: 'POST', body: JSON.stringify(data) }),
  joinTripByCode: (code) => request(`/group/join/${code}`, { method: 'POST' }),
  getGroupVotes: (tripId) => request(`/group/${tripId}/votes`),
  voteOnItem: (tripId, data) => request(`/group/${tripId}/votes`, { method: 'POST', body: JSON.stringify(data) }),
  getSettlements: (tripId) => request(`/group/${tripId}/settlements`),

  // What-If Simulator
  simulateTrip: (tripId, data) => request(`/trips/${tripId}/simulate`, { method: 'POST', body: JSON.stringify({ trip_id: tripId, ...data }) }),

  // Packing
  getPackingList: (tripId) => request(`/trips/${tripId}/packing`),
  addPackingItem: (tripId, data) => request(`/trips/${tripId}/packing`, { method: 'POST', body: JSON.stringify(data) }),
  togglePackingItem: (itemId) => request(`/packing/items/${itemId}/toggle`, { method: 'PUT' }),
  deletePackingItem: (itemId) => request(`/packing/items/${itemId}`, { method: 'DELETE' }),

  // Safety & Saved Places
  getSafetyReport: (destination) => request(`/safety/${encodeURIComponent(destination)}`),
  getSavedPlaces: () => request('/saved-places'),
  savePlace: (data) => request('/saved-places', { method: 'POST', body: JSON.stringify(data) }),
  deleteSavedPlace: (id) => request(`/saved-places/${id}`, { method: 'DELETE' }),

  // Chat
  sendChatMessage: (data) => request('/chat/message', { method: 'POST', body: JSON.stringify(data) }),
  getChatSessions: () => request('/chat/sessions'),
  getChatSessionDetail: (sessionId) => request(`/chat/sessions/${sessionId}`),
  deleteChatSession: (sessionId) => request(`/chat/sessions/${sessionId}`, { method: 'DELETE' })
};

