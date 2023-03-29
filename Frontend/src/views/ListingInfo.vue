<template>
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
      
      <br/>
      <div class="row">
        <div class="col"></div>

        <div class="col-2">
          <div class="input-group">
            <span class="input-group-text" id="basic-addon1">$</span>
            <input type="text" :class="{ 'form-control': true, 'me-2': true, 'is-invalid': !bidPriceIsValid }" style="width: 10%" id="bid-price" v-model="bidPrice">
            <div class="invalid-feedback text-nowrap">
              {{ bidErrMsg }}
            </div>
          </div>
        </div>

        <div class="col-auto">
          <button @click="placeBid" class="btn btn-outline-dark">Place Bid</button>
        </div>
      </div>

    </div>

  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'ListingInfo',
  props: {
    user: Object,
    token: String
  },
  data() {
    return {
      listingId: null,
      listingInfo: [],
      bidPrice: null,
      bidErrMsg: null,
      bidPriceIsValid: true,
    };
  },
  methods: {
    getListingInfo() {
      if (this.$route.query.listingID) {
        this.listingID = this.$route.query.listingID
        console.log("LISTING ID:", this.listingID)
        const path = 'http://127.0.0.1:5000/listing/' + this.listingID;
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
    placeBid() {
      if (!this.bidPrice) {
        this.bidErrMsg = "Please enter a bid price.";
        this.bidPriceIsValid = false;
      } else if (isNaN(this.bidPrice)) {
        this.bidErrMsg = "Please enter a valid bid price.";
        this.bidPriceIsValid = false;
      } else if (this.bidPrice <= this.listingInfo.highest_current_bid) {
        this.bidErrMsg = `Bid price must be higher than $${this.listingInfo.highest_current_bid}.`;
        this.bidPriceIsValid = false;
      } else {
        this.bidErrMsg = null;
        this.bidPriceIsValid = true;
        const bidDetails = {
          listing_id: this.listingID,
          user_id: this.user.uid,
          bid_price: Number(this.bidPrice),
        }
        console.log(bidDetails)
        
        axios.post('http://127.0.0.1:5015/bidforlisting', { data: bidDetails })
          .then((res) => {
            console.log(res.data.data);
          })
          .catch((error) => {
            console.error(error);
          });
      }
    },
  },
  created() {
    this.getListingInfo();
  },
}
</script>

<style></style>