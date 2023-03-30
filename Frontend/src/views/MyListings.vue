<template>
  <div>
    <h1>My Listings</h1>
    <div class="row d-flex mx-2" v-if="filteredListings && filteredListings.length > 0">
      <ItemCard v-for="listing in this.filteredListings" :listingData="listing" />
    </div>
    <div class="container-fluid d-flex justify-content-center align-items-center"
      style="height: calc(100vh - 200px); overflow: hidden;" v-else-if="searchInput || (!listings || listings.length == 0)">
      <p class="fs-5" style="color: #C6C6C6">You currently have no listings</p>
    </div>
    <div class="row d-flex mx-2" v-else>
      <ItemCard v-for="listing in this.listings" :listingData="listing" />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ItemCard from "../components/ItemCard.vue";
export default {
  name: 'MyListings',
  components: { ItemCard },
  props: {
    user: Object,
    token: String,
    searchInput: String,
  },
  data() {
    return {
      listings: [],
      filteredListings: [],
    }
  },
  watch: {
    searchInput: function(newVal, oldVal) {
      this.runSearch();
    }
  },
  methods: {
    getUserListings() {
      const path = `${this.$listing}/user/${this.user.uid}`;
      console.log(path)

      axios.get(path)
        .then((res) => {
          if (res.data.data) {
            this.listings = res.data.data.listings;
            console.log(this.listings);
          }
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
    this.getUserListings();
  },
}
</script>

<style></style>