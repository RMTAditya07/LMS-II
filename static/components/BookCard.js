export default { 
  template : `
  <div class="col-md-4" style="color:black">
    <div class="section-card">
      <div class="card mb-4 shadow-sm">
        <div class="card-body">
          <h5 class="card-title">{{ book.name }}</h5>
          <p class="card-subtitle mb-2 text-muted">Author: {{ book.authors }}</p>
          <p class="card-text">Section: {{ sectionName }}</p>
          <div class="btn-group mx-6">
            <!-- Conditional Rendering for Admins -->
            <template v-if="userRole === 'admin'">
              <router-link :to="'/edit_book/' + book.id" class="btn btn-warning">
                <img src="/static/components/assets/icons/edit-2-svgrepo-com.svg" width="24px" />
                
                </router-link>
                <button @click="deleteBook(book.id)" class="btn btn-danger">
                <img src="/static/components/assets/icons/delete-svgrepo-com.svg" width="24px" />
                </button>
                
                <a v-if="!isRequested" :href="'/api/download_pdf/' + book.id" class="btn btn-success">
                <img src="/static/components/assets/icons/download-minimalistic-svgrepo-com.svg" width="24px" />
              </a>
              <a v-if="!isRequested" :href="'/api/view_pdf/' + book.id" class="btn btn-primary">
                              <img src="/static/components/assets/icons/view-alt-1-svgrepo-com.svg" width="24px" />

              </a>
            </template>
            
            <!-- Conditional Rendering for Students -->
            <template v-else-if="userRole === 'student'">
              <button 
                :disabled="isRequested || isRequestLimitReached"                @click="handleRequest"
                class="btn btn-primary">
                {{ isRequested ? 'Requested' : 'Request' }}
              </button>
            </template>
            <button class="btn btn-info" @click="openReviewsModal">
                                          <img src="/static/components/assets/icons/movie-rating-review-svgrepo-com.svg" width="24px" />

            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
`,
  props: {
    book: {
      type: Object,
      required: true
    },
    userRole: {
      type: String,
      required: true
    },
    sectionName: String,
    isRequested: {
      type: Boolean,
      default: false
    },
    numRequestedBooks: {
      type: Number,
      required: true
    },
    requestLimit: {
      type: Number,
      default: 5
    }
  },
  computed: {
    isRequestLimitReached() {
      return this.numRequestedBooks >= this.requestLimit;
    }
  },  
  methods: {
    async handleRequest() {
      if (this.isRequestLimitReached) {
        alert('Request limit reached');
        return;
      }
      try {
        const response = await fetch(`/api/requests`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': localStorage.getItem('auth-token'),
          },
          body: JSON.stringify({ book_id: this.book.id })
        });
        const data = await response.json();
        if (response.ok) {
          this.$emit('update-request-status', this.book.id);
          window.location.reload();
        } else {
          alert(data.message || 'An error occurred');
        }
      } catch (error) {
        console.error('Error requesting book:', error);
      }
    },
    openReviewsModal() {
      this.$emit('show-reviews-modal', this.book.id, this.book.name);
    },
    deleteBook(bookId) {
      fetch(`/api/books/${bookId}`, {
        method: 'DELETE',
        headers: {
          'Authentication-Token': this.token,
          'Content-Type': 'application/json',
        },
      })
        .then(response => {
          if (response.ok) {
            this.fetchBooks();
          }
        });
    },
  }
};
