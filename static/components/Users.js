export default {
    template: `  <div class="user-container">
    <!-- Error message display -->
    <div v-if="error" class="alert alert-danger" role="alert">
      <strong>Error:</strong> {{ error }}
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="sr-only">Loading...</span>
      </div>
    </div>

    <!-- User list display -->
    <div v-else>
      <h2 class="mb-4 text-white">Users</h2>
      <div v-for="user in allUsers" :key="user.id" class="user-card card mb-3 text-black">
        <div class="card-body">
          <h5 class="card-title">{{ user.name }}</h5>
          <p class="card-text">
            <strong>Username:</strong> {{ user.username }}<br>
            <strong>Email ID:</strong> {{ user.email }}<br>
            <strong>Date Joined:</strong> {{ formatDate(user.date_joined) }}<br>
            <strong>Last Visited:</strong> {{ formatDate(user.last_visit_date) }}<br>
            <strong>Credit Points:</strong> {{ user.credit_points }}
          </p>
          <button class="btn btn-primary" v-if="!user.active" @click="approve(user.id)">Approve</button>
          <span v-if="user.active" class="badge bg-success">Approved</span>
        </div>
      </div>
    </div>
  </div>
    `,
  data() {
    return {
      allUsers: [],
      token: localStorage.getItem('auth-token'),
      error: null,
      loading: true,
    };
  },
  methods: {
    async approve(userId) {
      this.loading = true;
      try {
        const res = await fetch(`/api/user/activate/inst/${userId}`, {
          headers: {
            "Authentication-Token": this.token,
            'Content-Type': 'application/json',
          },
          method: 'POST'
        });
        const data = await res.json();
        if (res.ok) {
          alert(data.message);
          this.fetchUsers(); // Refresh the user list
        } else {
          this.error = data.message || 'Something went wrong';
        }
      } catch (e) {
        this.error = 'Failed to approve user';
      } finally {
        this.loading = false;
      }
    },
    async fetchUsers() {
      this.loading = true;
      try {
        const res = await fetch('/api/user', {
          headers: {
            'Authentication-Token': this.token,
          }
        });
        const data = await res.json();
        if (res.ok) {
          this.allUsers = data;
          console.log(data)
        } else {
          this.error = data.message || 'Failed to fetch users';
        }
      } catch (e) {
        this.error = 'Failed to fetch users';
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    }
  },
  async mounted() {
    await this.fetchUsers();
  }
};