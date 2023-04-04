<template>
  <div>
    <h1 class="pb-3">Listings</h1>
    <div class="row d-flex mx-2">
      <ItemCard v-for="listing in this.filteredListings" :listingData="listing"
        v-if="filteredListings && filteredListings.length > 0" :uid="user_id" />
      <div class="container-fluid d-flex justify-content-center align-items-center"
        style="height: calc(100vh - 200px); overflow: hidden;" v-else-if="searchInput">
        <p class="fs-5" style="color: #C6C6C6">No results found.</p>
      </div>
      <ItemCard v-for="listing in this.listings" :listingData="listing" v-else :uid="user_id" />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ItemCard from "../components/ItemCard.vue";
export default {
  name: 'Home',
  components: { ItemCard },
  props: {
    user: Object,
    uid: String,
    token: String,
    searchInput: String,
  },
  data() {
    return {
      listings: [],
      filteredListings: [],
      user_id: this.user.uid,
    };
  },
  watch: {
    searchInput: function (newVal, oldVal) {
      this.runSearch();
    }
  },
  methods: {
    getListings() {
      axios.get(this.$showListing)
        .then((res) => {
          this.listings = res.data.data.listings;
          console.log(res.data.data.listings);
        })
        .catch((error) => {
          console.error(error);
        });
    },
    runSearch() {
      if (this.searchInput) {
        console.log(this.searchInput)
        const keyword = this.searchInput.toLowerCase();
        const filteredData = this.listings.filter(item => {
          return item.listing_name.toLowerCase().includes(keyword);
        });

        this.filteredListings = filteredData;
      } else {
        this.filteredListings = [];
      }
    }
  },
  created() {
    this.getListings();
  },
}
</script>

<style></style>