export default {
  template : `  <div>
    <h3>Library Statistics</h3>
    <div class="container">
    <div class="container mt-4">
      <h1>Admin Dashboard</h1>

      <div class="statistics">
        <div class="stat" :style="{ backgroundColor: '#f8d7da' }">
          <div class="stat-circle">
            <p>{{ activeUsers }}</p>
          </div>
          <h2>Active Users</h2>
        </div>

        <div class="stat" :style="{ backgroundColor: '#d4edda' }">
          <div class="stat-circle">
            <p>{{ grantedRequests }}</p>
          </div>
          <h2>Granted Requests</h2>
        </div>
        <div class="stat" :style="{ backgroundColor: '#fff3cd' }">
          <div class="stat-circle">
            <p>{{ revokedRequests }}</p>
          </div>
          <h2>Revoked Requests</h2>
        </div>
        <div class="stat" :style="{ backgroundColor: '#e2e3e5' }">
          <div class="stat-circle">
          <p>{{ pendingRequests }}</p>
          </div>
          <h2>Pending Requests</h2>
          </div>
          
                    <div class="stat" :style="{ backgroundColor: '#f8d7da' }">
                      <div class="stat-circle">
                        <p>{{ rejectedRequests }}</p>
                      </div>
                      <h2>Rejected Requests</h2>
                    </div>
                  

        <div class="stat" :style="{ backgroundColor: '#cce5ff' }">
          <div class="stat-circle">
            <p>{{ ebooksIssued }}</p>
          </div>
          <h2>E-Books Issued</h2>
        </div>


        <div class="stat" :style="{ backgroundColor: '#f5c6cb' }">
          <div class="stat-circle">
            <p>{{ overdueRequests }}</p>
          </div>
          <h2>Overdue Requests</h2>
        </div>
    
        <!-- New Stats -->
            <div class="stat" :style="{ backgroundColor: '#e2e3e5' }">
              <div class="stat-circle">
                <p>{{ totalBooks }}</p>
              </div>
              <h2>Total Books</h2>
            </div>
  
            <div class="stat" :style="{ backgroundColor: '#d4edda' }">
              <div class="stat-circle">
                <p>{{ totalSections }}</p>
              </div>
              <h2>Total Sections</h2>
            </div>
      </div>
      </div>
    </div>
     <div class="row mb-4">
        <div class="col-md-6">
          <canvas id="usersEnrolledChart" class="chart"></canvas>
        </div>
        <div class="col-md-6">
          <canvas id="totalRequestsChart" class="chart"></canvas>
        </div>
      </div>
      <div class="row mb-4">
        <div class="col-md-6">
          <canvas id="booksBySectionChart" class="chart"></canvas>
        </div>
        <div class="col-md-6">
          <canvas id="requestsBySectionChart" class="chart"></canvas>
        </div>
      </div>
      <div class="row mb-4">
        <div class="col-md-6">
          <canvas id="mostRequestedBooksChart" class="chart"></canvas>
        </div>
        <div class="col-md-6">
          <canvas id="avgRatingByBookChart" class="chart"></canvas>
        </div>
      </div>
     
      
    </div>
  </div>
`,  data() {
    return {
      totalUsers: 0,
      booksBySection: {},
      totalBooks:0,
      totalSections:0,
      requestsBySection: {},
      mostRequestedBooks: [],
      avgRatingByBook: [],
      usersEnrolledEachMonth: {},
      totalRequestsEachMonth: {},
      activeUsers: 0,
      grantedRequests: 0,
      ebooksIssued: 0,
      revokedRequests: 0,
      overdueRequests: 0,
      pendingRequests: 0,
    };
  },
  async created() {
    await this.fetchStatistics();
    await this.fetchStatisticsData();
    this.renderCharts();
  },
  methods: {
    async fetchStatisticsData() {
      try {
        const [booksBySectionRes, requestsBySectionRes, totalUsersRes, mostRequestedBooksRes, avgRatingByBookRes, totalRequestsRes, totalBooksRes,totalSectionsRes] = await Promise.all([
          fetch('/api/stats?type=books_by_section').then(res => res.json()),
          fetch('/api/stats?type=requests_by_section').then(res => res.json()),
          fetch('/api/stats?type=total_users').then(res => res.json()),
          fetch('/api/stats?type=most_requested_books').then(res => res.json()),
          fetch('/api/stats?type=average_rating_by_book').then(res => res.json()),
          fetch('/api/stats?type=total_requests_each_month').then(res => res.json()),
          // fetch('/api/stats/users_enrolled_each_month').then(res => res.json()),
          fetch('/api/stats?type=total_users').then(res => res.json()),
          fetch('/api/stats?type=total_users').then(res => res.json())
        ]);

        // Filter out null values for avgRatingByBook
        const filteredAvgRatingByBook = Object.entries(avgRatingByBookRes)
          .filter(([name, rating]) => rating !== null)
          .map(([name, rating]) => ({ name, average_rating: rating }));

        console.log('Books by Section Response:', booksBySectionRes);
        console.log('Requests by Section Response:', requestsBySectionRes);
        console.log('Most Requested Books Response:', mostRequestedBooksRes);
        console.log('Average Rating by Book Response:', filteredAvgRatingByBook);
        // console.log('Users Enrolled Each Month Response:', usersEnrolledRes);
        console.log('Total Requests Each Month Response:', totalRequestsRes);

        this.booksBySection = booksBySectionRes;
        this.requestsBySection = requestsBySectionRes;
        this.totalUsers = totalUsersRes.total_users;
        this.mostRequestedBooks = Array.isArray(mostRequestedBooksRes) ? mostRequestedBooksRes : [];
        this.avgRatingByBook = filteredAvgRatingByBook;
        // this.usersEnrolledEachMonth = usersEnrolledRes;
        this.totalRequestsEachMonth = totalRequestsRes;
        this.totalBooks = totalBooksRes.total_books;
        this.totalSections = totalSectionsRes.total_sections;
      } catch (error) {
        console.error('Error fetching statistics:', error);
      }
    },
    async fetchStatistics() {
      try {
        const response = await fetch('/api/stats/admin', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth-token')}`
          }
        });
        const data = await response.json();
        this.activeUsers = data.activeUsers;
        this.grantedRequests = data.grantedRequests;
        this.ebooksIssued = data.ebooksIssued;
        this.revokedRequests = data.revokedRequests;
        this.rejectedRequests = data.rejectedRequests;
        this.overdueRequests = data.overdueRequests;
        this.pendingRequests = data.pendingRequests;
      } catch (error) {
        console.error('Error fetching statistics:', error);
      }
    },
    renderCharts() {
      // Books by Section Chart
      new Chart(document.getElementById('booksBySectionChart'), {
        type: 'bar',
        data: {
          labels: Object.keys(this.booksBySection),
          datasets: [{
            label: 'Number of Books by Section',
            data: Object.values(this.booksBySection),
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });

      // Requests by Section Chart
      new Chart(document.getElementById('requestsBySectionChart'), {
        type: 'bar',
        data: {
          labels: Object.keys(this.requestsBySection),
          datasets: [{
            label: 'Number of Requests by Section',
            data: Object.values(this.requestsBySection),
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });

      // Most Requested Books Chart
      new Chart(document.getElementById('mostRequestedBooksChart'), {
        type: 'doughnut',
        data: {
          labels: Array.isArray(this.mostRequestedBooks) ? this.mostRequestedBooks.map(book => book.name) : [],
          datasets: [{
            label: 'Most Requested Books',
            data: Array.isArray(this.mostRequestedBooks) ? this.mostRequestedBooks.map(book => book.count) : [],
            backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)'],
            borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)'],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });

      // Average Rating by Book Chart
      new Chart(document.getElementById('avgRatingByBookChart'), {
        type: 'line',
        data: {
          labels: Array.isArray(this.avgRatingByBook) ? this.avgRatingByBook.map(book => book.name) : [],
          datasets: [{
            label: 'Average Rating by Book',
            data: Array.isArray(this.avgRatingByBook) ? this.avgRatingByBook.map(book => book.average_rating) : [],
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });

      // Users Enrolled Each Month Chart
      new Chart(document.getElementById('usersEnrolledChart'), {
        type: 'line',
        data: {
          labels: Object.keys(this.usersEnrolledEachMonth),
          datasets: [{
            label: 'Users Enrolled Each Month',
            data: Object.values(this.usersEnrolledEachMonth),
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });

      // Total Requests Each Month Chart
      new Chart(document.getElementById('totalRequestsChart'), {
        type: 'line',
        data: {
          labels: Object.keys(this.totalRequestsEachMonth),
          datasets: [{
            label: 'Total Requests Each Month',
            data: Object.values(this.totalRequestsEachMonth),
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }
  }
}
