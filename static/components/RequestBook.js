export default{
  template : `   <div class="container mt-4">
    <h1>Requested Books</h1>

    <!-- Tabs for filtering requests -->
    <div class="btn-group" role="group" aria-label="Filter requests">
      <button 
        type="button" 
        class="btn btn-dark" 
        :class="{ active: activeTab === 'requested' }" 
        @click="filterRequests('requested')">
        Requested
      </button>
      <button 
        type="button" 
        class="btn btn-dark" 
        :class="{ active: activeTab === 'granted' }" 
        @click="filterRequests('granted')">
        Granted
      </button>
      <button 
        type="button" 
        class="btn btn-dark" 
        :class="{ active: activeTab === 'rejected' }" 
        @click="filterRequests('rejected')">
        Rejected
      </button>
      <button 
        type="button" 
        class="btn btn-dark" 
        :class="{ active: activeTab === 'revoked' }" 
        @click="filterRequests('revoked')">
        Revoked
      </button>
      <button 
        type="button" 
        class="btn btn-dark" 
        :class="{ active: activeTab === 'returned' }" 
        @click="filterRequests('returned')">
        Returned
      </button>
    </div>

    <!-- Table displaying filtered requests -->
    <div v-if="activeTab === 'requested'">
      <h2 class="mt-4">Requested Books</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Book Name</th>
            <th>Section Name</th>
            <th>Requested Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in filteredRequests" :key="request.id">
            <td>{{ request.book_name }}</td>
            <td>{{ request.section_name }}</td>
            <td>{{ request.requested_date }}</td>
            <td>{{ request.status }}</td>
          </tr>
          <tr v-if="!filteredRequests.length">
            <td colspan="3" class="text-center">No requests found for this status.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="activeTab === 'granted'">
      <h2 class="mt-4">My Books</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Author</th>
            <th>Section</th>
            <th>Borrowed Date</th>
            <th>Due Date</th>
            <th>Days Remaining</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="book in filteredRequests" :key="book.request_id">
            <td>{{ book.book_name }}</td>
            <td>{{ book.authors }}</td>
            <td>{{ book.section_name }}</td>
            <td>{{ book.borrowed_date }}</td>
            <td>{{ book.due_date }}</td>
            <td :class="{'text-danger': book.remaining_days === 'Overdue'}">{{ book.remaining_days }}</td>
            <td>
              <button @click="showFeedbackModal(book.request_id)" class="btn btn-danger" title="Return">
                <img src="/static/components/assets/icons/return-svgrepo-com.svg" width="24px" />
              </button>
              <a :href="'/api/books/' + book.book_id+'/download'" class="btn btn-primary" title="Download PDF" @click="handleDownloadClick()">
                <img src="/static/components/assets/icons/download-minimalistic-svgrepo-com.svg" width="24px" />
              </a>
              <a :href="'/api/books/' + book.book_id+'/view'" class="btn btn-info" title="View PDF">
                <img src="/static/components/assets/icons/view-alt-1-svgrepo-com.svg" width="24px" />
              </a>
            </td>
          </tr>
          <tr v-if="!filteredRequests.length">
            <td colspan="7" class="text-center">No requests found for this status.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="activeTab === 'rejected'">
      <h2 class="mt-4">Rejected Books</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Book Name</th>
            <th>Section Name</th>
            <th>Requested Date</th>
            <th>Rejected Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in filteredRequests" :key="request.id">
            <td>{{ request.book_name }}</td>
            <td>{{ request.section_name }}</td>
            <td>{{ request.requested_date }}</td>
            <td>{{ request.rejected_date }}</td>
            <td>{{ request.status }}</td>
          </tr>
          <tr v-if="!filteredRequests.length">
            <td colspan="3" class="text-center">No requests found for this status.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="activeTab === 'returned'">
      <h2 class="mt-4">Returned Books</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Book Name</th>
            <th>Section Name</th>
            <th>Borrowed Date</th>
            <th>Due Date</th>
            <th>Returned Date</th>
            <th>Feedback</th>
            <th>Ratings</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in filteredRequests" :key="request.id">
            <td>{{ request.book_name }}</td>
            <td>{{ request.section_name }}</td>
            <td>{{ request.borrowed_date }}</td>
            <td>{{ request.due_date }}</td>
            <td>{{ request.returned_date }}</td>
            <td>{{ request.feedback }}</td>
            <td>{{ request.ratings }}</td>
            <td>{{ request.status }}</td>
          </tr>
          <tr v-if="!filteredRequests.length">
            <td colspan="3" class="text-center">No requests found for this status.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="activeTab === 'revoked'">
      <h2 class="mt-4">Revoked Books</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Book Name</th>
            <th>Section Name</th>
            <th>Requested Date</th>
            <th>Revoked Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in filteredRequests" :key="request.id">
            <td>{{ request.book_name }}</td>
            <td>{{ request.section_name }}</td>
            <td>{{ request.requested_date }}</td>
            <td>{{ request.revoked_date }}</td>
            <td>{{ request.status }}</td>
          </tr>
          <tr v-if="!filteredRequests.length">
            <td colspan="3" class="text-center">No requests found for this status.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Feedback Modal -->
    <div class="modal fade" id="feedbackModal" tabindex="-1" role="dialog" aria-labelledby="feedbackModalLabel" aria-hidden="true">
      <div class="modal-dialog" role="document">
        <div class="modal-content" style="color:black;">
          <div class="modal-header">
            <h5 class="modal-title" id="feedbackModalLabel">Provide Feedback</h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close" @click="clearFeedback">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitFeedback">
              <div class="form-group">
                <label for="feedback">Feedback:</label>
                <textarea class="form-control" id="feedback" v-model="feedback" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label for="ratings">Ratings:</label>
                <div class="form-check form-check-inline" v-for="rating in [1, 2, 3, 4, 5]" :key="rating">
                  <input class="form-check-input" type="radio" :value="rating" v-model="ratingValue">
                  <label class="form-check-label">{{ rating }}</label>
                </div>
              </div>
              <input type="hidden" v-model="currentRequestId">
              <button type="submit" class="btn btn-primary">Submit Return</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
`,
data() {
  return {
    requestedBooks: [], // All requests fetched from the API
    filteredRequests: [], // Requests filtered by status
    activeTab: 'requested', // The currently active tab
    feedback: '',
    ratingValue: null,
    currentRequestId: null,
    token: localStorage.getItem('auth-token')
  };
},
mounted() {
  this.fetchRequestedBooks();
},
methods: {
  async fetchRequestedBooks() {
    try {
      const response = await fetch('/api/requests/', {
        headers: {
          'Authentication-Token': this.token,
        }
      });
      const data = await response.json();
      this.requestedBooks = data.requests;
      this.filterRequests(this.activeTab); // Initialize the filtered requests
    } catch (error) {
      console.error('Error fetching requested books:', error);
    }
  },
  filterRequests(status) {
    this.activeTab = status;
    this.filteredRequests = this.requestedBooks.filter(request => request.status === status);
  },
  showFeedbackModal(requestId) {
    this.currentRequestId = requestId;
    $('#feedbackModal').modal('show');
  },
  async submitFeedback() {
    try {
      const response = await fetch(`/api/requests/return/${this.currentRequestId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ feedback: this.feedback, ratings: this.ratingValue })
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      $('#feedbackModal').modal('hide');
      this.clearFeedback();
      this.fetchRequestedBooks(); // Refresh the list
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  },
  clearFeedback() {
    this.feedback = '';
    this.ratingValue = null;
    this.currentRequestId = null;
  },
  handleDownloadClick(bookId) {
    // Trigger a page refresh after download link is clicked
    setTimeout(() => {
      window.location.reload();
    }, 100); // Delay the refresh slightly to ensure the download starts
  } 
}
};