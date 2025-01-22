export default {
template : `
   <div class="container mt-4">
    <h1>Books Management Dashboard</h1>

    <div class="btn-group" role="group" aria-label="Toggle requests">
      <button 
        type="button" 
        class="btn btn-dark" 
        :class="{ active: activeTab === 'requested' }" 
        @click="setActiveTab('pending')">
        Pending Requests
      </button>
      <button 
        type="button" 
        class="btn btn-dark" 
        :class="{ active: activeTab === 'granted' }" 
        @click="setActiveTab('approved')">
        Approved Requests
      </button>
      <button 
        type="button" 
        class="btn btn-dark" 
        :class="{ active: activeTab === 'returned' }" 
        @click="setActiveTab('returned')">
        Returned Requests
      </button>
      <button 
        type="button" 
        class="btn btn-dark" 
        :class="{ active: activeTab === 'revoked' }" 
        @click="setActiveTab('revoked')">
        Revoked Requests
      </button>
      <button 
        type="button" 
        class="btn btn-dark" 
        :class="{ active: activeTab === 'rejected' }" 
        @click="setActiveTab('rejected')">
        Rejected Requests
      </button>
    </div>
    
    <div class="requests-tables mt-4">
      <!-- Pending Requests Table -->
      <table v-if="activeTab === 'pending'" class="table">
        <thead>
          <tr>
            <th scope="col">Book Name</th>
            <th scope="col">Student Name</th>
            <th scope="col">Section Name</th>
            <th scope="col">Requested Date</th>
            <th scope="col">Status</th>
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in pendingRequests" :key="request.id">
            <td>{{ request.book_name }}</td>
            <td>{{ request.name }}</td>
            <td>{{ request.section_name }}</td>
            <td>{{ request.requested_date }}</td>
            <td>{{ request.status }}</td>
            <td>
              <div class="btn-group" role="group">
                <button @click="approveRequest(request.id)" class="btn btn-success btn-sm">Approve</button>
                <button @click="rejectRequest(request.id)" class="btn btn-danger btn-sm">Reject</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Approved Requests Table -->
      <table v-if="activeTab === 'approved'" class="table">
        <thead>
          <tr>
            <th scope="col">Book Name</th>
            <th scope="col">Student Name</th>
            <th scope="col">Section Name</th>
            <th scope="col">Requested Date</th>
            <th scope="col">Borrowed Date</th>
            <th scope="col">Due Date</th>
            <th scope="col">Remaining Days</th>
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in approvedRequests" :key="request.id">
            <td>{{ request.book_name }}</td>
            <td>{{ request.name }}</td>
            <td>{{ request.section_name }}</td>
            <td>{{ request.requested_date }}</td>
            <td>{{ request.borrowed_date }}</td>
            <td>{{ request.due_date }}</td>
            <td :class="{'text-danger': request.remaining_days === 'Overdue'}">
              {{ request.remaining_days }}
            </td>
            <td>
              <button @click="revokeRequest(request.id)" class="btn btn-danger btn-sm">Revoke</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Returned Requests Table -->
      <table v-if="activeTab === 'returned'" class="table">
        <thead>
          <tr>
            <th scope="col">Book Name</th>
            <th scope="col">Student Name</th>
            <th scope="col">Section Name</th>
            <th scope="col">Requested Date</th>
            <th scope="col">Returned Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in returnedRequests" :key="request.id">
            <td>{{ request.book_name }}</td>
            <td>{{ request.name }}</td>
            <td>{{ request.section_name }}</td>
            <td>{{ request.requested_date }}</td>
            <td>{{ request.returned_date }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Revoked Requests Table -->
      <table v-if="activeTab === 'revoked'" class="table">
        <thead>
          <tr>
            <th scope="col">Book Name</th>
            <th scope="col">Student Name</th>
            <th scope="col">Section Name</th>
            <th scope="col">Requested Date</th>
            <th scope="col">Revoked Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in revokedRequests" :key="request.id">
            <td>{{ request.book_name }}</td>
            <td>{{ request.name }}</td>
            <td>{{ request.section_name }}</td>
            <td>{{ request.requested_date }}</td>
            <td>{{ request.revoked_date }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Rejected Requests Table -->
      <table v-if="activeTab === 'rejected'" class="table">
        <thead>
          <tr>
            <th scope="col">Book Name</th>
            <th scope="col">Student Name</th>
            <th scope="col">Section Name</th>
            <th scope="col">Requested Date</th>
            <th scope="col">Rejected Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in rejectedRequests" :key="request.id">
            <td>{{ request.book_name }}</td>
            <td>{{ request.name }}</td>
            <td>{{ request.section_name }}</td>
            <td>{{ request.requested_date }}</td>
            <td>{{ request.rejected_date }}</td>
          </tr>
        </tbody>
      </table>

      <!-- No Data Message -->
      <div v-if="!requestsForActiveTab.length" class="no-requests text-center">
        <h2 class="display-4">All Clear!</h2>
        <p class="lead">There are currently no requests for this status.</p>
        <img src="/static/components/assets/images/confetti.gif" alt="Confetti celebration" class="confetti">
      </div>
    </div>
  </div>
`,
  data() {
    return {
      pendingRequests: [],
      approvedRequests: [],
      returnedRequests: [],
      revokedRequests: [],
      rejectedRequests: [],
      pendingRequestsCount: 0,
      activeTab: 'pending',
      token: localStorage.getItem('auth-token'),
    };
  },
  computed: {
    requestsForActiveTab() {
      switch (this.activeTab) {
        case 'pending':
          return this.pendingRequests;
        case 'approved':
          return this.approvedRequests;
        case 'returned':
          return this.returnedRequests;
        case 'revoked':
          return this.revokedRequests;
        case 'rejected':
          return this.rejectedRequests;
        default:
          return [];
      }
    }
  },
  mounted() {
    this.fetchRequests('requested');
    this.fetchRequests('granted');
    this.fetchRequests('returned');
    this.fetchRequests('revoked');
    this.fetchRequests('rejected');
  },
  methods: {
    async fetchRequests(status) {
      try {
        const response = await fetch(`/api/requests/${status}`, {
          headers: {
            'Authentication-Token': this.token,
          },
        });
        const data = await response.json();
        this[`${
          status === 'requested' ? 'pendingRequests' :
          status === 'granted' ? 'approvedRequests' :
          status === 'returned' ? 'returnedRequests' :
          status === 'revoked' ? 'revokedRequests' :
          'rejectedRequests'
        }`] = data.requests;
        if (status === 'requested') this.pendingRequestsCount = data.count;
      } catch (error) {
        console.error(`Error fetching ${status} requests:`, error);
      }
    },
    async approveRequest(requestId) {
      try {
        await fetch(`/api/requests/${requestId}/approve`, { method: 'POST' });
        this.fetchRequests('requested');
        this.fetchRequests('granted');
      } catch (error) {
        console.error('Error approving request:', error);
      }
    },
    async rejectRequest(requestId) {
      try {
        await fetch(`/api/requests/${requestId}/reject`, { method: 'POST' });
        this.fetchRequests('requested');
        this.fetchRequests('rejected');
      } catch (error) {
        console.error('Error rejecting request:', error);
      }
    },
    async revokeRequest(requestId) {
      try {
        await fetch(`/api/requests/${requestId}/revoke`, { method: 'POST' });
        this.fetchRequests('granted');
        this.fetchRequests('revoked');
      } catch (error) {
        console.error('Error revoking request:', error);
      }
    },
    setActiveTab(tab) {
      this.activeTab = tab;
    }
  }
};
