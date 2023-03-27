<template>
  <div>
    <h1 class="pb-3">Listings</h1>
    <div class="row d-flex mx-2">
      <ItemCard v-for="listing in this.listings" :listingData="listing" />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ItemCard from "../components/ItemCard.vue";
export default {
  name: 'Home',
  data() {
    return {
      listings: [],
    };
  },
  components: { ItemCard },
  methods: {
    getListings() {
      const path = 'http://127.0.0.1:5000/listing';
      axios.get(path)
        .then((res) => {
          this.listings = res.data.data.listings;
          console.log(res.data.data.listings);
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
  created() {
    this.getListings();
  },
}
</script>

<style></style>