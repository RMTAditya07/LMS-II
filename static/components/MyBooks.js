export default {
    template : `
<div class="container mt-4">
    <h1 class="mb-4">My Books</h1>
    <table v-if="acceptedBooks.length" class="table">
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
        <tr v-for="book in acceptedBooks" :key="book.request_id">
          <td>{{ book.book_name }}</td>
          <td>{{ book.authors }}</td>
          <td>{{ book.section_name }}</td>
          <td>{{ book.borrowed_date }}</td>
          <td>{{ book.due_date }}</td>
          <td>{{ book.remaining_days }}</td>
          <td>
            <button @click="showFeedbackModal(book.request_id)" class="btn btn-danger" title="Return">
              <img src="/static/components/assets/icons/return-svgrepo-com.svg" width="24px" />
            </button>
            <a :href="'/api/books/download_pdf/' + book.book_id" class="btn btn-primary" title="Download PDF">
              <img src="/static/components/assets/icons/download-minimalistic-svgrepo-com.svg" width="24px" />
            </a>
            <a :href="'/api/books/view_pdf/' + book.book_id" class="btn btn-info" title="View PDF">
              <img src="/static/components/assets/icons/view-alt-1-svgrepo-com.svg" width="24px" />
            </a>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="text-center">
      <p>Start collecting your favorites!</p>
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
`,  data() {
    return {
      acceptedBooks: [], // Should be populated with data from an API
      feedback: '',
      ratingValue: null,
      currentRequestId: null,
      pdfSrc: '',
      token: localStorage.getItem('auth-token'),

    };
  },
  methods: {
    async fetchAcceptedBooks() {
      try {
        const response = await fetch('/api/requests/accepted-books',
          {
            headers: {
              'Authentication-Token': this.token,
            }
          }
        );
        const data = await response.json();
        this.acceptedBooks = data.accepted_books;
      } catch (error) {
        console.error('Error fetching accepted books:', error);
      }
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
        });XMLDocument
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        $('#feedbackModal').modal('hide');
        this.clearFeedback();
        window.location.reload();
      } catch (error) {
        console.error('Error submitting feedback:', error);
      }
    },
    clearFeedback() {
      this.feedback = '';
      this.ratingValue = null;
      this.currentRequestId = null;
    },
  
  },
  mounted() {
    this.fetchAcceptedBooks();
  }
}
