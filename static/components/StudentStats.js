export default {
    template :  `
    <div class="container mt-4">
    <h1>Student Statistics</h1>

    <div class="statistics">
      <div class="stat" :style="{ backgroundColor: '#f8d7da' }">
        <div class="stat-circle">
          <p>{{ totalBooksBorrowed }}</p>
        </div>
        <h2>Total Books Borrowed</h2>
      </div>

      <div class="stat" :style="{ backgroundColor: '#d4edda' }">
        <div class="stat-circle">
          <p>{{ booksReturnedOnTime }}</p>
        </div>
        <h2>Books Returned On Time</h2>
      </div>

      <div class="stat" :style="{ backgroundColor: '#cce5ff' }">
        <div class="stat-circle">
          <p>{{ averageRating.toFixed(1) }}</p>
        </div>
        <h2>Average Rating</h2>
      </div>

      <div class="stat" :style="{ backgroundColor: '#fff3cd' }">
        <div class="stat-circle">
          <p>{{ pendingRequests }}</p>
        </div>
        <h2>Pending Requests</h2>
      </div>

      <div class="stat" :style="{ backgroundColor: '#f5c6cb' }">
        <div class="stat-circle">
          <p>{{ overdueBooks }}</p>
        </div>
        <h2>Overdue Books</h2>
      </div>
      <div class="stat" :style="{ backgroundColor: '#e2e3e5' }">
          <div class="stat-circle">
            <p>{{ favoriteSection }}</p>
          </div>
          <h2>Favorite Section</h2>
        </div>
      </div>
    </div>
  </div>
`,
  data() {
    return {
      totalBooksBorrowed: 0,
      booksReturnedOnTime: 0,
      averageRating: 0,
      pendingRequests: 0,
      overdueBooks: 0,
      favoriteSection: 'Loading...',
    };
  },
  mounted() {
    this.fetchStatistics();
  },
  methods: {
    async fetchStatistics() {
      try {
        const response = await fetch('/api/stats/student', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth-token')}`
          }
        });
        const data = await response.json();
        this.totalBooksBorrowed = data.totalBooksBorrowed;
        this.booksReturnedOnTime = data.booksReturnedOnTime;
        this.averageRating = data.averageRating;
        this.pendingRequests = data.pendingRequests;
        this.overdueBooks = data.overdueBooks;
        this.favoriteSection = data.favoriteSection;
      } catch (error) {
        console.error('Error fetching statistics:', error);
      }
    }
  }
};
