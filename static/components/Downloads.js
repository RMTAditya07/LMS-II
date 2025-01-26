export default {
    template: `
    <div class="download-container">
    <h2>Welcome Admin</h2>
    <div class="button-group">
      <button @click='downloadSections' :disabled="isWaiting">
        Download Sections Report
      </button>
      <button @click='downloadBooks' :disabled="isWaiting">
        Download Books Report
      </button>
      <button @click='downloadBookRequests' :disabled="isWaiting">
        Download Book Requests Report
      </button>
    </div>
    <span v-if='isWaiting' class="waiting-message">Waiting...</span>
  </div> `,
  data() {
    return {
      isWaiting: false,
    }
  },
  methods: {
    async downloadSections() {
      this.isWaiting = true;
      const res = await fetch('/api/reports/export/csv?type=sections');
      const data = await res.json();
      if (res.ok) {
        const taskId = data['task-id'];
        const intv = setInterval(async () => {
          const csv_res = await fetch(`/api/reports/get_csv/${taskId}`);
          if (csv_res.ok) {
            this.isWaiting = false;
            clearInterval(intv);
            window.location.href = `/api/reports/get_csv/${taskId}`;
          }
        }, 1000);
      } else {
        this.isWaiting = false;
      }
    },
    async downloadBooks() {
      this.isWaiting = true;
      const res = await fetch('/api/reports/export/csv?type=books');
      const data = await res.json();
      if (res.ok) {
        const taskId = data['task-id'];
        const intv = setInterval(async () => {
          const csv_res = await fetch(`/api/reports/get_csv/${taskId}`);
          if (csv_res.ok) {
            this.isWaiting = false;
            clearInterval(intv);
            window.location.href = `/api/reports/get_csv/${taskId}`;
          }
        }, 1000);
      } else {
        this.isWaiting = false;
      }
    },
    async downloadBookRequests() {
      this.isWaiting = true;
      const res = await fetch('/api/reports/export/csv?type=book_requests');
      const data = await res.json();
      if (res.ok) {
        const taskId = data['task-id'];
        const intv = setInterval(async () => {
          const csv_res = await fetch(`/api/reports/get_csv/${taskId}`);
          if (csv_res.ok) {
            this.isWaiting = false;
            clearInterval(intv);
            window.location.href = `/api/reports/get_csv/${taskId}`;
          }
        }, 1000);
      } else {
        this.isWaiting = false;
      }
    },
  },
}