<template>
  <div>
    <h1>{{ listingInfo.listing_name }}</h1>
    <div class="container p-3">
      <div class="row my-3">
        <h4>Highest Current Bid: {{ listingInfo.highest_current_bid }}</h4>
        <p class="mb-3 fw-medium fs-5">Auction Ends on <span class="fw-medium">{{
          timeConverter(listingInfo.auction_end_datetime) }}</span></p>
      </div>
      <div class="row mt-2">
        <div class="col-5">
          Image here
        </div>
        <div class="col-7 border border-dark-subtle rounded p-3">
          <h5>Product Description</h5>
          <hr>
          {{ listingInfo.listing_description }}
        </div>
      </div>
      <div class="mt-5 d-flex justify-content-end">
        <div class="d-flex align-items-center me-2">
          <span>$</span>
        </div>
        <input type="text" class="form-control me-2" style="width: 10%" id="bid-price">
        <button type="submit" class="btn btn-outline-dark">Place Bid</button>
      </div>

    </div>

  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'ListingInfo',
  data() {
    return {
      listingInfo: [],
    };
  },
  methods: {
    getListingInfo() {
      if (this.$route.query.listingID) {
        var listingID = this.$route.query.listingID
        console.log("LISTING ID:", listingID)
        const path = 'http://127.0.0.1:5000/listing/' + listingID;
        console.log("PATH:", path)
        axios.get(path)
          .then((res) => {
            this.listingInfo = res.data.data;
            console.log(this.listingInfo);
          })
          .catch((error) => {
            console.error(error);
          });
      }
    },
    timeConverter(UNIX_timestamp) {
      var a = new Date(UNIX_timestamp * 1000);
      var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      var year = a.getFullYear();
      var month = months[a.getMonth()];
      var date = a.getDate();
      var hour = a.getHours();
      var time = "";
      if (hour > 12) {
        time = "pm"
      } else {
        time = "am"
      }
      var min = a.getMinutes();
      if (min == 0) {
        min = "00"
      }
      var sec = a.getSeconds();
      // var formattedDate = date + '/' + a.getMonth() + '/' + year + ' (' + (hour - 12) + "." + min + time + ")";
      var formattedDate = date + ' ' + month + ' ' + year + ' (' + hour + ':' + min + time + ")";
      return formattedDate;
    },
  },
  created() {
    this.getListingInfo();
  },
}
</script>

<style></style>