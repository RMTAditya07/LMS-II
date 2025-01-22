import BookCard from "./BookCard.js";
import ReviewsModal from "./ReviewsModal.js";

export default {
  template: `
    <div class="container mt-4">
      <h1 class="mb-4">All Books</h1>
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
       <BookCard
        v-for="book in filteredBooks"
        :key="book.id"
        :book="book"
        :userRole="userRole"
        :section-name="sections[book.section_id]?.name" 
        :isRequested="requestedBooks.includes(book.id)"
        :numRequestedBooks="numRequestedBooks"
  :requestLimit="requestLimit"
        @update-request-status="updateRequestStatus"
        @show-reviews-modal="openReviewsModal"
      />
      </div>
      <ReviewsModal
      :show="isReviewsModalVisible"
      :bookId="selectedBookId"
      :bookName="selectedBookName"
      @close="closeReviewsModal"
    />
      </div>
    </div>
  `,
  components: {
    BookCard,
    ReviewsModal
  },
  computed: {
    isAdmin() {
      return this.userRole === 'admin';
    },
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
  data() {
    return {
      numRequestedBooks: 0,
      books: [],
      sections: {},
      searchBook:'',
      token: localStorage.getItem('auth-token'),
      userRole: localStorage.getItem('role'),
      isReviewsModalVisible: false,
      requestedBooks: [],
      selectedBookId: null,
      selectedBookName: '',
      requestLimit: 5

    };
  },
  mounted() {
    this.fetchBooks();
    this.fetchSections();
  },
  methods: {
    fetchBooks() {
      const role = localStorage.getItem('role');
      fetch('/api/books', {
        headers: {
          'Authentication-Token': this.token,
          'Role': role
        }
      })
      .then(response => response.json())
      .then(data => {
        this.books = data.books || []; // Ensure this.books is an array
        this.numRequestedBooks = data.num_requested_books;
        console.log("bum : ",this.numRequestedBooks)
        this.requestedBooks = data.requested_books || [];

      })
      .catch(error => {
        console.error('Error fetching books:', error);
      });
    },
    async fetchSections() {
      try {
        const response = await fetch('/api/sections', {
          headers: {
            'Authentication-Token': this.token,
            'Role': this.userRole
          }
        });
        const data = await response.json();
        this.sections = data.reduce((acc, section) => {
          acc[section.id] = section;
          return acc;
        }, {});
      } catch (error) {
        console.error('Error fetching sections:', error);
      }
    },
    async updateRequestStatus(bookId) {
      if (!this.requestedBooks.includes(bookId)) {
        this.requestedBooks.push(bookId);
      }

      // Move requested books to the end of the array
      this.books.sort((a, b) => {
        if (this.requestedBooks.includes(a.id) && !this.requestedBooks.includes(b.id)) return 1;
        if (!this.requestedBooks.includes(a.id) && this.requestedBooks.includes(b.id)) return -1;
        return 0;
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

