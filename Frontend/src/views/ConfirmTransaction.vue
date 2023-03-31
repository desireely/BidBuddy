<template>
  <div>
    <div>
      <h1>{{ listingInfo.listing_name }}</h1>
      <div class="container p-3">
        <div class="row">
          <h4>Highest Current Bid: ${{ listingInfo.highest_current_bid }}</h4>
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

        <div v-if="user.uid == listingInfo.userid || user.uid == listingInfo.highest_current_bidder_userid">
          <h4>Confirm Transaction?</h4>
          <br/>
          <button @click="confirmTransaction" class="btn btn-outline-dark">Yes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'ConfirmTransaction',
  props: {
    user: Object,
    token: String
  },
  data() {
    return {
      listingID: null,
      listingInfo: [],
    }
  },
  created() {
    this.getListingInfo();
  },
  methods: {
    confirmTransaction() {
      const info = {
        user_id: this.user.uid,
        data: this.$route.query.data
      }
      axios.post('http://127.0.0.1:5009/confirm', info)
        .then(response => {
          console.log(response.data)
        })
        .catch(error => {
          console.log(error)
        })
    },
    getListingInfo() {
      if (this.$route.query.listingID) {
        this.listingID = this.$route.query.listingID
        console.log("LISTING ID:", this.listingID)
        const path = `${this.$listing}/${this.listingID}`;
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
        hour = hour - 12
        time = "pm"
      } else {
        time = "am"
      }
      var min = a.getMinutes();
      if (min.toString().length == 1) {
        min = min.toString() + "0"
      }

      var sec = a.getSeconds();
      var formattedDate = date + '/' + (a.getMonth() + 1) + '/' + year + ' (' + (hour) + "." + min + time + ")";
      // var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min;
      // console.log(time);
      return formattedDate;
    },
  }
}
</script>

<style></style>