export default {
  template : `
    <div class="col-md-4 sidebar" v-if="is_login">
      <button @click="goBack" class="btn btn-transparent">
        <img src="/static/components/assets/icons/back-svgrepo-com.svg" width="24px" />
      </button>
      <div class="nav-item" v-if="is_login">
        <router-link class="nav-link" to="/home">Home <span class="sr-only">(current)</span></router-link>
      </div>
      <div class="nav-item" v-if="!is_login">
        <router-link class="nav-link" to="/login">Login</router-link>
      </div>
      <div class="nav-item" v-if="role == 'admin'">
        <router-link class="nav-link" to="/users">Users</router-link>
      </div>
      <div class="nav-item" v-if="role == 'admin'">
        <router-link class="nav-link" to="/request-dashboard">Requests</router-link>
      </div>
      <div class="nav-item" v-if="role == 'admin'">
        <router-link class="nav-link" to="/stats">Stats</router-link>
      </div>
      <div class="nav-item" v-if="role == 'admin'">
        <router-link class="nav-link" to="/downloads">Downloads</router-link>
      </div>
      <div class="nav-item" v-if="role == 'student'">
        <router-link class="nav-link" to="/books">All Books</router-link>
      </div>
      <div class="nav-item" v-if="role == 'student'">
        <router-link class="nav-link" to="/sections">All Sections</router-link>
      </div>
      <div class="nav-item" v-if="role == 'student'">
        <router-link class="nav-link" to="/my-requests">My Books</router-link>
      </div>
      <div class="nav-item" v-if="role == 'student'">
        <router-link class="nav-link" to="/my-stats">Stats</router-link>
      </div>
    
      <div class="sidebar-widget" v-if="is_login && role == 'student'">
        <p class="text-lime">Credit Points: {{ creditPoints }}</p>
      </div>
      <form @submit.prevent="logout" class="logout-btn" v-if="is_login">
        <button type="submit" class="btn btn-danger">Logout</button>
      </form>
    </div>
    <div class="col-md-10 content">
    <div class="container mt-4">
      <router-view />
    </div>
    </div>
  
`,
  data() {
    return {
      role: localStorage.getItem('role'),
      is_login: localStorage.getItem('auth-token'),
      creditPoints: 0
    };
  },
  created() {
    if (this.is_login) {
      this.fetchUserCreditPoints();
    }
  },
  methods: {
    goBack() {
      window.history.back();
    },
    async logout() {
      const userId = sessionStorage.getItem('user_id');
      const url = '/api/user/last-visit';  // Replace with your actual endpoint
      const data = { user_id: userId };

      try {
        const response = await fetch(url, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': this.is_login,
          },
          body: JSON.stringify(data),
        });

        if (!response.ok) {
          throw new Error('Failed to update last visit time');
        }

        localStorage.removeItem('role');
        localStorage.removeItem('auth-token');
        sessionStorage.removeItem('user_id');
        this.$router.push({ path: '/' });
      } catch (error) {
        console.error('Error:', error);
      }
    },
    async fetchUserCreditPoints() {
      try {
        const response = await fetch('/api/user/credit-points', {
          headers: {
            'Authentication-Token': this.is_login,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch credit points');
        }

        const data = await response.json();
        this.creditPoints = data.creditPoints || 0;
      } catch (error) {
        console.error('Error fetching credit points:', error);
      }
    }
  }
}
