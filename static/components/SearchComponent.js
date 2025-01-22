
export default {
    template : `<div class="mb-4">
    <input
      type="text"
      class="form-control"
      id="searchInput"
      placeholder="Search..."
      v-model="searchText"
    />
  </div>
`,
  name: "SearchComponent",
  data() {
    return {
      searchText: ""
    };
  },
  methods: {
    emitSearch() {
      this.$emit("search", this.searchText.toLowerCase());
    }
  },
  watch: {
    searchText() {
      this.emitSearch();
    }
  }
}