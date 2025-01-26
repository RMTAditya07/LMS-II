export default {
  template :`
    <div v-if="show" class="modal fade show d-block" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content" style="color:black">
        <div class="modal-header">
          <h5 class="modal-title">Reviews for Book "{{ bookName }}"</h5>
          <button type="button" class="close" @click="closeModal" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <div v-if="reviews.length">
            <div v-for="review in reviews" :key="review.id" class="review-item">
              <p><strong>{{ review.username }}</strong> - Rating: {{ review.rating }}/5</p>
              <p>{{ review.feedback }}</p>
            </div>
            <hr>
            <div v-if="consolidatedRating !== null">
              <h6>Consolidated Rating: {{ consolidatedRating }}/5</h6>
            </div>
          </div>
          <div v-else>
            <p>No reviews available for this book.</p>
          </div>
          <!-- Show the form only if inputFlag is true -->
          <div v-if="inputFlag" class="mt-4">
            <h6>Submit Your Review</h6>
            <form @submit.prevent="submitReview">
              <div class="form-group">
                <label for="rating">Rating (1-5):</label>
                <input v-model="rating" type="number" min="1" max="5" class="form-control" id="rating" required>
              </div>
              <div class="form-group">
                <label for="feedback">Feedback:</label>
                <textarea v-model="feedback" class="form-control" id="feedback" rows="3" required></textarea>
                <small v-if="feedback.length > 0 && feedback.length < 10" class="form-text text-danger">
                  Feedback must be at least 10 characters long.
                </small>
              </div>
              <button type="submit" class="btn btn-primary">Submit Review</button>
            </form>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
        </div>
      </div>
    </div>
  </div>
`,
  props: {
    show: Boolean,
    bookId: Number,
    bookName: String,
    inputFlag: Boolean // New prop to control form visibility
  },
  watch: {
    show(newVal) {
      if (newVal && this.bookId) {
        this.fetchReviews();
      }
    }
  },
  data() {
    return {
      reviews: [],
      consolidatedRating: null,
      feedback: '',
      rating: null
    };
  },
  async created() {
    if (this.bookId) {
      await this.fetchReviews();
    }
  },
  methods: {
    async fetchReviews() {
      try {
        const response = await fetch(`/api/books/${this.bookId}/reviews`, {
          headers: {
            'Authentication-Token': localStorage.getItem('auth-token')
          }
        });
        const data = await response.json();
        
        this.reviews = data.reviews || [];
  
        if (this.reviews.length > 0) {
          this.calculateConsolidatedRating();
        } else {
          this.consolidatedRating = null;
        }
      } catch (error) {
        console.error('Error fetching reviews:', error);
      }
    },
    calculateConsolidatedRating() {
      if (this.reviews.length > 0) {
        const totalRating = this.reviews.reduce((sum, review) => {
          const rating = review.rating || 0;
          return sum + rating;
        }, 0);
        this.consolidatedRating = (totalRating / this.reviews.length).toFixed(1);
      }
    },
    async submitReview() {
      if (this.feedback.length < 10) {
        alert('Feedback must be at least 10 characters long.');
        return;
      }
      
      try {
        const response = await fetch(`/api/books/${this.bookId}/reviews`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': localStorage.getItem('auth-token')
          },
          body: JSON.stringify({ rating: this.rating, feedback: this.feedback })
        });
        const data = await response.json();
        
        if (response.ok) {
          this.fetchReviews();
          this.feedback = '';
          this.rating = null;
        } else {
          alert(data.message || 'An error occurred');
        }
      } catch (error) {
        console.error('Error submitting review:', error);
      }
    },
    closeModal() {
      this.$emit('close');
    }
  }
}
