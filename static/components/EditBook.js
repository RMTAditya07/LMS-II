export default {
    template : `
  <div class="container">
    <h2>Edit Book</h2>
    <form @submit.prevent="saveChanges" enctype="multipart/form-data">
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="bookName">Name:</label>
            <input type="text" class="form-control" v-model="book.name" id="bookName" name="name" />
          </div>
        </div>
        <div class="col-md-6">
          <div class="form-group">
            <label for="bookSection">Section:</label>
             <select class="form-control" id="bookSection" name="section" required>
                                    <option v-for="section in sections" :value="section.name">{{ section.name }}</option>
                                </select>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="bookAuthor">Author:</label>
            <input type="text" class="form-control" v-model="book.authors" id="bookAuthor" name="author" />
          </div>
        </div>
        <div class="col-md-6">
          <div class="form-group">
            <label for="bookCredits">Credit Cost:</label>
            <input type="number" class="form-control" v-model="book.credit_cost" id="bookCredits" name="credit_cost" />
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="bookFile">Upload Book File (PDF):</label>
            <input type="file" class="form-control-file" @change="handleFileUpload" id="bookFile" name="pdf_file" accept=".pdf" />
          </div>
        </div>
        <div class="col-md-6">
          <div class="form-group">
            <label for="bookFilename">Filename:</label>
            <input class="form-control" v-model="book.file_name" id="bookFilename" name="filename" />
          </div>
        </div>
      </div>
      <button type="submit" class="btn btn-primary" id="save-btn">Save Changes</button>
    </form>
    <div v-if="successMessage" class="alert alert-success" role="alert">
      Changes saved successfully!
    </div>
  </div>
`,
  data() {
    return {
      book: {
        name: '',
        section_id: null,
        authors: '',
        credit_cost: '',
        file_name: ''
      },
      sections: [],
      successMessage: false,
      file: null,
      token: localStorage.getItem('auth-token'),

    };
  },
  mounted() {
    this.fetchSections();
    this.fetchBook();
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('success')) {
      this.successMessage = true;
    }
  },
  methods: {
    fetchBook() {
      const bookId = this.$route.params.id;
      fetch(`/api/books/${bookId}`)
        .then(response => response.json())
        .then(data => {
          this.book = data;
        });
    },
    fetchSections() {
      fetch('/api/sections', {
        method: 'GET',
        headers: {
            'Authentication-Token': this.token,
          }}
        )
        .then(response => response.json())
        .then(data => {
          this.sections = data;
        });
    },
    handleFileUpload(event) {
      this.file = event.target.files[0];
    },
    saveChanges() {
      const formData = new FormData();
      formData.append('name', this.book.name);
      formData.append('section_id', this.book.section_id);
      formData.append('authors', this.book.authors);
      formData.append('credit_cost', this.book.credit_cost);
      formData.append('file_name', this.book.file_name);
      if (this.file) {
        formData.append('pdf_file', this.file);
      }

      fetch(`/api/books/${this.$route.params.id}`, {
        method: 'PUT',
        body: formData
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            this.successMessage = true;
            setTimeout(() => {
              this.successMessage = false;
            }, 2000);
          }
        });
    }
  }
}
