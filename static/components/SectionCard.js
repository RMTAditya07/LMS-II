export default {
    template:`
      <div class="col-md-4 mb-3" style="color:black">
    <div class="card">
      <div class="section-card">
        <div class="card-body">
          <h5 class="card-title">Name : {{ section.name }}</h5>
          <p class="card-text">Description : {{ section.description }}</p>
          <router-link :to="{ name: 'user_section_books', params: { section_id: section.id } }" class="btn btn-primary">
            View Books
          </router-link>
        </div>
      </div>
    </div>
  </div>
    `,
    props: {
      section: {
        type: Object,
        required: true
      }
    }
  };