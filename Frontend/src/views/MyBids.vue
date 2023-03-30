<template>
  <div>
    <h1>My Bids</h1>
    <div class="row d-flex mx-2" v-if="listings && listings.length > 0">
      <ItemCard v-for="listing in this.listings" :listingData="listing" />
    </div>
    <div class="container-fluid d-flex justify-content-center align-items-center"
      style="height: calc(100vh - 200px); overflow: hidden;" v-else>
      <p class="fs-5" style="color: #C6C6C6">You currently have no bids.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ItemCard from "../components/ItemCard.vue";
export default {
  name: 'MyBids',
  components: { ItemCard },
  props: {
    user: Object,
    token: String
  },
  data() {
    return {
      listings: [],
    }
  },
  methods: {
    getUserBids() {
      const path = `http://127.0.0.1:5002/showdetailsofbids/${this.user.uid}`;
      console.log(path)

      axios.get(path)
        .then((res) => {
          if (res.data.data) {
            this.listings = res.data.data;
            console.log(this.listings);
          }
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
  created() {
    this.getUserBids();
  },
}
</script>

<style></style>