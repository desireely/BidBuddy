<template>
  <div>
    <h1>{{ listingInfo.listing_name }}</h1>
    <h5 class="" style="color: #C6C6C6">Listed by: {{ sellerName }}</h5>
    <div class="container p-3">
      <div class="row">
        <h4>{{ listingInfo.highest_current_bid ? "Highest Bid: $" + listingInfo.highest_current_bid : "Starting Bid: $" +
          listingInfo.starting_bid }}</h4>
        <p class="mb-3 fw-medium fs-5">Auction Ends on <span class="fw-medium">{{
          timeConverter(listingInfo.auction_end_datetime) }}</span></p>
      </div>
      <div class="row mt-2">
        <div class="col-5">
          <img :src="listingInfo.listing_image_url" style='height: 100%; width: 100%; object-fit: contain'>
        </div>
        <div class="col-7 border border-dark-subtle rounded p-3">
          <h5>Product Description</h5>
          <hr>
          {{ listingInfo.listing_description }}
        </div>
      </div>

      <br />
      <div class="row" v-if="user.uid != listingInfo.userid">
        <div class="col"></div>

        <div class="col-3">
          <div class="input-group">
            <span class="input-group-text" id="basic-addon1">$</span>
            <input type="text" :class="{ 'form-control': true, 'me-2': true, 'is-invalid': !bidPriceIsValid }"
              style="width: 10%" id="bid-price" v-model="bidPrice">
            <div class="invalid-feedback text-nowrap">
              {{ bidErrMsg }}
            </div>
          </div>
        </div>

        <div class="col-auto">
          <button @click="placeBid" class="btn btn-outline-dark">Place Bid</button>
        </div>
      </div>
      <div class="row" v-else-if="listingInfo.status == 'closed' && listingInfo.transaction_status == 'open' && !('can_reopen' in listingInfo)">
        <div class="col"></div>
        <div class="col-2"></div>

        <div class="col-auto">
          <button @click="displayQRCode" class="btn btn-outline-dark">Confirm Transaction</button>
        </div>
      </div>
      <div class="row" v-else-if="listingInfo.status == 'closed' && listingInfo.can_reopen">
        <div class="col"></div>

        <div class="col-5">
          <div class="input-group">
            <span class="input-group-text" id="basic-addon1">New Bidding End Date</span>
            <input type="datetime-local" :class="{ 'form-control': true, 'is-invalid': !endDateIsValid }"
              v-model="endDate" id="ending-date">
            <div class="invalid-feedback">
              {{ endDateErrMsg }}
            </div>
          </div>
        </div>

        <div class="col-auto">
          <button @click="validateEndDate()" class="btn btn-outline-dark">Reopen Listing</button>
        </div>
      </div>
    </div>

    <div
      v-if="user.uid == listingInfo.userid && encoded_string && listingInfo.status == 'closed' && listingInfo.transaction_status == 'open'">
      <h4>Scan the QR Code to confirm transaction:</h4>
      <div class="row">
        <div class="col">
          <img :src="`data:image/png;base64,${encoded_string}`" />
        </div>
      </div>
    </div>

    <div class="modal fade" id="successModal" tabindex="-1" aria-labelledby="successModalLabel" aria-hidden="true"
      ref="successModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="successModalLabel">{{ bidStatus }}</h1>
          </div>
          <div class="modal-body">
            {{ bidCreation }}
          </div>
          <div class="modal-footer">
            <router-link to="/mybids">
              <button type="button" class="btn btn-outline-dark" data-bs-dismiss="modal">My Bids</button>
            </router-link>
            <button type="button" class="btn btn-dark" data-bs-dismiss="modal">Close</button>
          </div>
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
      bidStatus: null,
      bidCreation: null,

      listingID: null,
      sellerName: this.$route.query.username,

      listingInfo: [],
      bidPrice: null,
      bidErrMsg: null,
      bidPriceIsValid: true,
      encoded_string: null,

      endDate: null,
      endDateIsValid: true,
      endDateErrMsg: null,
    };
  },
  methods: {
    validateEndDate() {
      if (!this.endDate) {
        this.endDateErrMsg = "Field is required.";
        this.endDateIsValid = false;
      } else if (new Date(this.endDate) <= new Date()) {
        this.endDateErrMsg = "End date must be after current date.";
        this.endDateIsValid = false;
      } else {
        this.endDateErrMsg = null;
        this.endDateIsValid = true;
        this.reopen();
      }
    },
    reopen() {
      axios.post(this.$reopenlisting, { auction_end_datetime: this.endDate })
        .then((res) => {
            console.log(res.data);
            this.bidStatus = "Listing Reopened!";
            this.bidCreation = `You have reopened ${this.listingInfo.listing_name}!`

            this.endDate = null;
            this.endDateErrMsg = null;
            var myModal = new bootstrap.Modal(this.$refs.successModal)
            var modalToggle = this.$refs.successModal;
            myModal.show(modalToggle);
          })
          .catch((error) => {
            console.error(error);
            this.bidStatus = "Listing was not reopened!";
            this.bidCreation = "There was an error reopening your listing."

            var myModal = new bootstrap.Modal(this.$refs.successModal)
            var modalToggle = this.$refs.successModal;
            myModal.show(modalToggle);
          });
    },
    displayQRCode() {
      console.log("Current User: ", this.user.uid)
      console.log("Seller: ", this.listingInfo.userid)
      console.log("Buyer: ", this.listingInfo.highest_current_bidder_userid)

      if (this.user.uid == this.listingInfo.userid) {
        const transactionInfo = {
          seller_id: this.user.uid,
          buyer_id: this.listingInfo.highest_current_bidder_userid,
          listing_id: this.listingID,
        }
        axios.post(this.$qrCode, transactionInfo)
          .then(response => {
            this.encoded_string = response.data.data;
          })
          .catch(error => {
            console.log(error)
          });
      }
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

        axios.post(this.$bidForListing, bidDetails)
          .then((res) => {
            console.log(res.data.data);
            this.bidStatus = "Bid placed!";
            this.bidCreation = `You have placed a bid of $${this.bidPrice} for ${this.listingInfo.listing_name}!`

            this.bidPrice = null;
            var myModal = new bootstrap.Modal(this.$refs.successModal)
            var modalToggle = this.$refs.successModal;
            myModal.show(modalToggle);
          })
          .catch((error) => {
            console.error(error);
            if (error.response.data.message.startsWith("An error occurred while creating the bid. Minimum bid increment")) {
              this.bidErrMsg = `Minimum bid increment is ${error.response.data.message.match(/\$.*/)[0]}`
              this.bidPriceIsValid = false;
            } else {
              this.bidStatus = "Bid was not placed!";
              this.bidCreation = "There was an error placing your bid."

              var myModal = new bootstrap.Modal(this.$refs.successModal)
              var modalToggle = this.$refs.successModal;
              myModal.show(modalToggle);
            }
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