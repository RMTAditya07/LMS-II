export default {
    template : `
  <div>
    <div class="row align-items-center">
      <div class="col-md-6">
        <h1 class="mb-4">Sections</h1>
      </div>
      <div class="col-md-6 text-right">
        <button v-if="isAdmin" type="button" class="btn btn-primary" @click="showAddSectionModal">Add Section</button>
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
      <div v-if="sections.length === 0">
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
              <img src="/static/components/assets/icons/add-book-svgrepo-com.svg" width="24px" />
                
              </button>
              <router-link :to="'/edit_section/' + section.id" v-if="this.userRole === 'admin'" class="btn btn-warning">
              <img src="/static/components/assets/icons/edit-2-svgrepo-com.svg" width="24px" />
              </router-link>
              <router-link :to="{ name: 'Section', params: { id: section.id } }" class="btn btn-info">
                <img src="/static/components/assets/icons/view-alt-1-svgrepo-com.svg" width="24px" />
                </router-link>
                <button @click="deleteSection(section.id)" v-if="this.userRole === 'admin'" class="btn btn-danger">
                
                <img src="/static/components/assets/icons/delete-svgrepo-com.svg" width="24px" />
              </button>

            </div>
          </div>
        </div>
      </div>
    </div>

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
                                <input
                                    type="text"
                                    class="form-control"
                                    :value="currentSectionName"
                                    disabled
                                />
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
                            <input type="hidden" id="sectionName" name="section" v-model="currentSectionName">
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
`,  data() {
    return {
      sections: [],
      searchText: '',
      currentSectionId: null,
      currentSectionName: '',
      newSection: {
        title: '',
        description: '',
      },
      userRole: localStorage.getItem('role'),
      token: localStorage.getItem('auth-token'),
    };
  },
  computed: {
    filteredSections() {
      return this.sections.filter(section => {
        const searchTextLower = this.searchText.toLowerCase();
        return (
          section.name.toLowerCase().includes(searchTextLower) ||
          (section.description && section.description.toLowerCase().includes(searchTextLower))
        );
      });
    },
    isAdmin() {
      // Check if the user role is 'admin'
      return this.userRole === 'admin';
    }

  },
  methods: {
    fetchSections() {
      fetch('/api/sections',{
        headers: {
            'Authentication-Token': this.token,
          },
        })
        .then(response => response.json())
        .then(data => {
          this.sections = data;
        })
        .catch(error => {
          console.error('Error fetching sections:', error);
        });
    },
    showAddBookModal(sectionId, sectionName) {
      this.currentSectionId = sectionId;
      this.currentSectionName = sectionName;
    //   this.newBook.section_id = sectionId;
      $('#addBookModal').modal('show');
    },
    addBook() {
        const form = document.getElementById('addBookForm');
        const formData = new FormData(form);
        var fileInput = document.getElementById("bookFile");
        if (fileInput.files.length > 0) {
            formData.append("pdf_file", fileInput.files[0]);
        }
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
    showAddSectionModal() {
      $('#addSectionModal').modal('show');
    },
    addSection() {
        const form = document.getElementById('addSectionForm');
        const formData = new FormData(form);
        formData.append('section_id', this.currentSectionId);
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
  },
  mounted() {
    this.fetchSections();
  },
}
