import SearchComponent from './SearchComponent.js';
import BookCard from './BookCard.js';
import SectionCard from './SectionCard.js';
import ReviewsModal from './ReviewsModal.js';

export default {
  template : `
  <div class="container">
    <h1 class="mt-3 mb-4 text-white">Welcome to the Library</h1>

    <!-- Include Search Component -->
 <div class="mb-4">
      <input
        type="text"
        class="form-control"
        v-model="searchBook"
        placeholder="Search..."
      />
    </div>
    <div class="row align-items-center">
    <div class="col-md-6">
    <h3 class="text-white my-4">Newly Released Books</h3>
      </div>
      <div class="col-md-6 text-right">
        <router-link to="/books" class="btn btn-primary">View All</router-link>
      </div>
    </div>
    <div class="row flex-nowrap overflow-auto">
      <!-- Include Book Card Component -->
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

    <div class="row align-items-center">
      <div class="col-md-6">
        <h3 class="text-white my-4">Search by Categories</h3>
      </div>
      <div class="col-md-6 text-right">
        <router-link to="/sections" class="btn btn-primary">View All</router-link>
      </div>
    </div>

    <!-- Search Input -->
    <div class="mb-4">
      <input
        type="text"
        class="form-control"
        v-model="searchText"
        placeholder="Search..."
      />
    </div>

    <!-- Section Cards -->
    <div class="row">
      <div v-if="Array.isArray(sections) && sections.length === 0">
        <h2 style="color:red;">No Sections available!</h2>
      </div>
      <div v-for="section in filteredSections" :key="section.id" class="col-md-4 mb-4 section-card" style="color:black">
        <div class="card h-100">
          <div class="card-body">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h5 class="card-title">{{ section.name }}</h5>
                <p class="card-text">
                  <strong>Description:</strong> {{ section.description }}
                </p>
              </div>
              <div>
                <span class="badge badge-info">{{ section.book_count }} Books</span>
              </div>
            </div>
            <div class="d-flex justify-content-between">
              <button v-if="isAdmin" 
                class="btn btn-primary"
                @click="showAddBookModal(section.id, section.name)"
              >
                Add Book
              </button>
              <router-link :to="{ name: 'Section', params: { id: section.id } }" class="btn btn-primary">
                View Books
              </router-link>
            </div>
          </div>
        </div>
      </div>
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
    SearchComponent,
    BookCard,
    SectionCard,
    ReviewsModal
  },
  data() {
    return {
      books: [],
      sections: {},
      searchText: '',
      searchBook: '',
      userRole: localStorage.getItem('role'),
      token: localStorage.getItem('auth-token'),
      requestedBooks: [],
      numRequestedBooks : 0,
      isReviewsModalVisible: false,
      selectedBookId: null,
      selectedBookName: '',
      requestLimit: 5
    };
  },
  async created() {
    // Fetch books and sections data when the component is created
    await this.fetchBooks();
    await this.fetchSections();
  },
  computed: {
    isAdmin() {
      return this.userRole === 'admin';
    },
    filteredSections() {
      return Object.values(this.sections).filter(section => {
        const searchTextLower = this.searchText.toLowerCase();
        return (
          section.name.toLowerCase().includes(searchTextLower) ||
          (section.description && section.description.toLowerCase().includes(searchTextLower))
        );
      });
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
  methods: {
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
    async fetchBooks() {
      try {
        const response = await fetch('/api/books', {
          headers: {
            'Authentication-Token': this.token,
            'Role': this.userRole
          }
        });
        const data = await response.json();
        this.books = data.books;
        this.numRequestedBooks = data.num_requested_books;
        this.requestedBooks = data.requested_books || [];
      } catch (error) {
        console.error('Error fetching books:', error);
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
};
