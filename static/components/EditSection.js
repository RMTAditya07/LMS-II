export default {
    template: `
      <div class="container">
        <h2>Edit Section</h2>
        <form @submit.prevent="saveChanges">
          <div class="form-group">
            <label for="name">Name:</label>
            <input type="text" class="form-control" v-model="section.name" id="name" name="name" />
          </div>
          <div class="form-group">
            <label for="description">Description:</label>
            <textarea class="form-control" v-model="section.description" id="description" name="description"></textarea>
          </div>
  
          <div v-if="section.books.length">
            <h3>Edit Books</h3>
            <table class="table table-bordered text-white">
              <thead>
                <tr>
                  <th>Select to remove the books</th>
                  <th>Title</th>
                  <th>Author</th>
                  <!-- Add more columns as needed -->
                </tr>
              </thead>
              <tbody>
                <tr v-for="book in section.books" :key="book.id">
                  <td>
                    <input type="checkbox" class="book-checkbox" :value="book.id" v-model="selectedBooks" />
                  </td>
                  <td>{{ book.name }}</td>
                  <td>{{ book.authors }}</td>
                  <!-- Add more columns as needed -->
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else>
            <div id="no-books-message" class="text-center">
              <p>No books in this section.</p>
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
        section: {
          name: '',
          description: '',
          books: []
        },
        selectedBooks: [],
        successMessage: false
      };
    },
    mounted() {
      this.fetchSection();
    },
    methods: {
      fetchSection() {
        // Replace with actual API call
        fetch('/api/section/' + this.$route.params.id)
          .then(response => response.json())
          .then(data => {
            console.log('Fetched section data:', data); // Debugging line
            this.section = data;
          })
          .catch(error => console.error('Error fetching section:', error));
      },
      saveChanges() {
        // Replace with actual API call
        fetch('/api/sections/' + this.$route.params.id, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': localStorage.getItem('auth-token')
          },
          body: JSON.stringify({
            name: this.section.name,
            description: this.section.description,
            removedBooks: this.selectedBooks
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            this.successMessage = true;
            setTimeout(() => {
              this.successMessage = false;
            }, 2000);
          }
        })
        .catch(error => console.error('Error saving changes:', error));
      }
    }
  }
  