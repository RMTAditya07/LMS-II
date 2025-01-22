export default {
    template : `<div>
    <h1 style="color:yellow;">Admin Dashboard</h1>

    <!-- Section Table -->
    <div style="margin-bottom:16px; overflow:hidden;">
      <div class="row align-items-center">
        <div class="col-md-6">
          <h2 class="mb-3">Sections</h2>
        </div>
        <div class="col-md-6 text-right">
          <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#addSectionModal">Add Section</button>
          <router-link to="/sections" class="btn btn-primary">View All Sections</router-link>
        </div>
      </div>

      <div class="table-responsive d-inline-block">
        <table v-if="sections.length" class="table table-bordered text-white">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>No. of Books</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="section in latestSections" :key="section.id">
              <td>{{ section.id }}</td>
              <td>{{ section.name }}</td>
              <td>{{ section.book_count }}</td>
              <td>
                <router-link :to="'/edit_section/' + section.id" class="btn btn-primary">Edit</router-link>
                <router-link :to="'/section/' + section.id" class="btn btn-info">View</router-link>
                <button @click="deleteSection(section.id)" class="btn btn-danger">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
        <h2 v-else class="flex align-items-center" style="text-align: center; color:red;">No Sections available!</h2>
      </div>
    </div>

    <!-- Book Table -->
    <div>
      <div class="row align-items-center">
        <div class="col-md-6">
          <h2 class="mb-3">Books</h2>
        </div>
        <div class="col-md-6 text-right">
          <button class="btn btn-primary" data-toggle="modal" data-target="#addBookModal">Add Book</button>
          <router-link to="/books" class="btn btn-primary">View All Books</router-link>
        </div>
      </div>
      <div class="table-responsive">
        <table v-if="latestBooks.length" class="table table-bordered text-white">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Author</th>
              <th>Section</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="book in latestBooks" :key="book.id">
              <td>{{ book.id }}</td>
              <td>{{ book.name }}</td>
              <td>{{ book.authors }}</td>
              <td>{{ book.section_id }}</td>
              <td>
                <router-link :to="'/edit_book/' + book.id" class="btn btn-primary">Edit</router-link>
                <a :href="'/api/view_pdf/' + book.id" class="btn btn-secondary">View</a>
                <button @click="deleteBook(book.id)" class="btn btn-danger">Delete</button>
                <a :href="'/api/download_pdf/' + book.id" class="btn btn-info">Download PDF</a>

              </td>
            </tr>
          </tbody>
        </table>
        <h2 v-else class="flex align-items-center" style="text-align: center; color:red;">No Books available!</h2>
      </div>
    </div>

    <!-- Modals (unchanged) -->
    <!-- Add Book Modal -->
    <div class="modal fade" id="addBookModal" tabindex="-1" role="dialog" aria-labelledby="addBookModalLabel" aria-hidden="true">
      <div class="modal-dialog" role="document">
        <div class="modal-content" style="color:black;">
          <div class="modal-header">
            <h5 class="modal-title" id="addBookModalLabel">Add Book</h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <!-- Book Details Form -->
            <form id="addBookForm" enctype="multipart/form-data">
              <div class="form-group">
                <label for="bookTitle">Title</label>
                <input type="text" class="form-control" id="bookTitle" name="title" required>
              </div>
              <div class="form-group">
                <label for="bookAuthor">Author</label>
                <input type="text" class="form-control" id="bookAuthor" name="author" required>
              </div>
              <div class="form-group">
                <label for="bookSection">Section</label>
                <select class="form-control" id="bookSection" name="section" required>
                  <option v-for="section in sections" :value="section.name">{{ section.name }}</option>
                </select>
              </div>
              <div class="form-group">
                <label for="bookName">File Name</label>
                <input type="text" class="form-control" id="bookName" name="filename" required>
              </div>
              <div class="form-group">
                <label for="bookCredits">Credits</label>
                <input type="number" class="form-control" id="bookCredits" name="credits" required>
              </div>
              <div class="form-group">
                <label for="bookFile">Upload Book File (PDF)</label>
                <input type="file" class="form-control-file" id="bookFile" name="pdf_file" accept=".pdf" required>
              </div>
              <!-- Hidden input for Section ID -->
              <input type="hidden" id="sectionId" name="section_id">
            </form>
            <!-- Success message -->
            <div id="successMessage" class="alert alert-success" role="alert" style="display: none">
              Book added successfully!
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="addBook">Save Book</button>
          </div>
        </div>
      </div>
    </div>
    <!-- Add Section Modal -->
    <div class="modal fade" id="addSectionModal" tabindex="-1" role="dialog" aria-labelledby="addSectionModalLabel" aria-hidden="true">
      <div class="modal-dialog" role="document">
        <div class="modal-content" style="color:black;">
          <div class="modal-header">
            <h5 class="modal-title" id="addSectionModalLabel">Add Section</h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <!-- Section Details Form -->
            <form id="addSectionForm">
              <div class="form-group">
                <label for="sectionName">Section Name</label>
                <input type="text" class="form-control" id="sectionName" name="section_name" required>
              </div>
              <div class="form-group">
                <label for="sectionDesc">Section Description</label>
                <input type="text" class="form-control" id="sectionDesc" name="section_desc" required>
              </div>
            </form>
            <!-- Success message -->
            <div id="sectionSuccessMessage" class="alert alert-success" role="alert" style="display: none">
              Section added successfully!
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="addSection">Save Section</button>
          </div>
        </div>
      </div>
    </div>
  </div>
`,
  data() {
    return {
      sections: [],
      books_with_requested_count: [],
      token: localStorage.getItem('auth-token'),
    }
  },
  computed: {
    latestSections() {
      return this.sections.slice(-5);  // Get the latest 5 sections
    },
    latestBooks() {
      return this.books_with_requested_count.slice(-5);  // Get the latest 5 books
    }
  },
  methods: {
    fetchSections() {
      fetch('/api/sections', {
        headers: {
          'Authentication-Token': this.token,
        }
      })
        .then(response => response.json())
        .then(data => {
          this.sections = data;
          console.log(this.sections)
        });
    },
    fetchBooks() {
      fetch('/api/books', {
        headers: {
          'Authentication-Token': this.token,
        }
      })
        .then(response => response.json())
        .then(data => {
          this.books_with_requested_count = data.books;
          console.log("books :", this.books_with_requested_count)
        });
    },
    addBook() {
      const form = document.getElementById('addBookForm');
      const formData = new FormData(form);
      var fileInput = document.getElementById("bookFile");
      formData.append("pdf_file", fileInput.files[0]);
      fetch('/api/books', {
        method: 'POST',
        headers: {
          'Authentication-Token': this.token,
        },
        body: formData,
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            this.fetchBooks();
            document.getElementById('successMessage').style.display = 'block';
            setTimeout(() => {
              document.getElementById('successMessage').style.display = 'none';
              $('#addBookModal').modal('hide');
            }, 2000);
          }
        });
    },
    addSection() {
      const form = document.getElementById('addSectionForm');
      const formData = new FormData(form);
      fetch('/api/sections', {
        method: 'POST',
        headers: {
          'Authentication-Token': this.token,
        },
        body: formData,
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            this.fetchSections();
            document.getElementById('sectionSuccessMessage').style.display = 'block';
            setTimeout(() => {
              document.getElementById('sectionSuccessMessage').style.display = 'none';
              $('#addSectionModal').modal('hide');
            }, 2000);
          }
        });
    },
    deleteSection(sectionId) {
      fetch(`/api/sections/${sectionId}`, {
        method: 'DELETE',
        headers: {
          'Authentication-Token': this.token,
          'Content-Type': 'application/json',
        },
      })
        .then(response => {
          if (response.ok) {
            this.fetchSections();
          }
        });
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
  },
  created() {
    this.fetchSections();
    this.fetchBooks();
  }
}
