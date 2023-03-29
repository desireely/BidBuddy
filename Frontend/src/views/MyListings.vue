<template>
  <div>
    <h1>My Listings</h1>
    <div class="row d-flex mx-2" v-if="listings && listings.length > 0">
      <ItemCard v-for="listing in this.listings" :listingData="listing" />
    </div>
    <div class="container-fluid d-flex justify-content-center align-items-center"
      style="height: calc(100vh - 200px); overflow: hidden;" v-else>
      <p class="fs-5" style="color: #C6C6C6">You currently have no listings</p>
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
    token: Object
  },
  data() {
    return {
      listings: [],
    }
  },
  methods: {
    getUserListings() {
      const path = `http://127.0.0.1:5000/listing/user/99`;
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
  },
  created() {
    this.getUserListings();
  },
}
</script>

<style></style>