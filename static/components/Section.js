import BookCard from './BookCard.js'
import NoBookComponent from './NoBookComponent.js';
import SearchComponent from './SearchComponent.js';
import ReviewsModal from './ReviewsModal.js';

export default {
    
    template : ` <div>
    
    <h1 class="mb-4 text-white">Books in Section "{{ sectionName }}"</h1>
    <div v-if="books.length">
      <!-- Include the search component if needed -->
       <div class="mb-4">
      <input
        type="text"
        class="form-control"
        v-model="searchBook"
        placeholder="Search..."
      />
    </div>
    <div v-if="numRequestedBooks !== null && numRequestedBooks !== undefined && this.userRole !== 'admin'" class="alert alert-info" role="alert">
  You can borrow {{ Math.max(0, 5 - numRequestedBooks) }} more books.
</div>
      <div class="row">
        <!-- Iterate over the books to create book cards -->
        <BookCard
          v-for="book in filteredBooks"
          :key="book.id"
          :book="book"
          :section-name="sectionName"
          :isRequested="requestedBooks.includes(book.id)"
          :requestLimit="requestLimit"
          :user-role="userRole"
          :numRequestedBooks="numRequestedBooks"
          @show-reviews-modal="openReviewsModal"
        />
      </div>
    </div>
    <div v-else>
      <!-- Include the no book component if no books are available -->
      <NoBookComponent />
    </div>
  <ReviewsModal
      :show="isReviewsModalVisible"
      :bookId="selectedBookId"
      :bookName="selectedBookName"
      @close="closeReviewsModal"
    />  
  </div>
`,
  components: {
    BookCard,
    NoBookComponent,
    ReviewsModal
  },
  data() {
    return {
      books: [],
      requestedBooks: [],
      searchBook:'',
      sectionId: this.$route.params.id, // Get section ID from route params
      sectionName : this.$route.params.name,
      userRole: localStorage.getItem('role'),
      numRequestedBooks: 0,
      selectedBookId: null,
      selectedBookName: '',
      isReviewsModalVisible: false,

    };
  },
  mounted() {
    this.fetchBooks();
  },
  computed:{
    filteredBooks() {
      return Object.values(this.books).filter(book => {
        const searchTextLower = this.searchBook.toLowerCase();
        return (
          book.name.toLowerCase().includes(searchTextLower) ||
          (book.authors && book.authors.toLowerCase().includes(searchTextLower)) 
        );
      });
    },
  },
  methods: {
    fetchBooks() {
      fetch(`/api/section/${this.sectionId}`)
        .then(response => response.json())
        .then(data => {
          this.books = data.books;
          this.numRequestedBooks = data.num_requested_books;
          this.sectionName = data.name;
          this.requestedBooks = data.requested_books || [];

        });
    },
    openReviewsModal(bookId, bookName) {
      this.selectedBookId = bookId;
      this.selectedBookName = bookName;
      this.isReviewsModalVisible = true;
    },
    closeReviewsModal() {
      this.isReviewsModalVisible = false;
      this.selectedBookId = null;
      this.selectedBookName = '';
    }
  }
}