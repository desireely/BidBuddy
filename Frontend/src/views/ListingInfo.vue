<template>
  <div>
    <h1>{{ listingInfo.listing_name }}</h1>
    <span class="badge bg-black mb-2"
      v-if="listingInfo.highest_current_bidder_userid && listingInfo.highest_current_bidder_userid == user.uid">You're the
      highest bidder!</span>
    <h5 class="" style="color: #C6C6C6">Listed by: {{ sellerName }}</h5>
    <p class="mb-1" style="color: #C6C6C6">Posted on: {{ timeConverter(listingInfo.datetime_created) }}</p>
    <div class="container p-3">
      <div class="row">
        <div class="col">
          <h4>{{ listingInfo.highest_current_bid ? "Highest Bid: $" + listingInfo.highest_current_bid : "Starting Bid: $"
            +
            listingInfo.starting_bid }}</h4>
          <p class="fw-medium fs-5 mb-0">
            <i class="bi bi-clock"></i> Time Left: {{ timeLeft(listingInfo.auction_end_datetime) }} ({{
              timeConverter(listingInfo.auction_end_datetime) }})
          </p>
        </div>
        <div class="col text-end"><button class="btn btn-outline-dark"><i class="bi bi-trash3-fill"></i> Delete</button>
        </div>
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
      <div class="row" v-if="user.uid != listingInfo.userid && listingInfo.status == 'open'">
        <div class="col"></div>

        <div class="col-5 col-md-3">
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
          <button @click="placeBid" class="btn btn-dark">Place Bid</button>
        </div>
      </div>
      <div class="row justify-content-end"
        v-else-if="user.uid == listingInfo.userid && listingInfo.status == 'closed' && listingInfo.transaction_status == 'open' && !('can_reopen' in listingInfo) && listingInfo.highest_current_bid">
        <div class="col-auto">
          <button @click="displayQRCode" class="btn btn-outline-dark">Confirm Transaction</button>
        </div>
      </div>
      <div class="row justify-content-end"
        v-else-if="user.uid == listingInfo.userid && listingInfo.status == 'closed' && listingInfo.can_reopen && listingInfo.highest_current_bid">
        <div class="col-lg-6 col-md-8 col-sm-8 col-8">
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
      v-if="user.uid == listingInfo.userid && encoded_string && listingInfo.status == 'closed' && listingInfo.transaction_status == 'open' && !('can_reopen' in listingInfo) && listingInfo.highest_current_bid">
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
            <router-link to="/mybids" v-if="myBids">
              <button type="button" class="btn btn-outline-dark" data-bs-dismiss="modal">My Bids</button>
            </router-link>
            <router-link to="/mylistings" v-else>
              <button type="button" class="btn btn-outline-dark" data-bs-dismiss="modal">My Listings</button>
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
import { db } from "../../firebaseConfig.js"

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

      myBids: true,
    };
  },
  mounted() {
    setInterval(() => {
      this.$forceUpdate();
    }, 1000);
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
      axios.post(`${this.$reopenlisting}/${this.$route.query.listingID}`, { auction_end_datetime: this.endDate })
        .then((res) => {
          console.log(res.data);
          this.myBids = false;
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

            const docRef = db.collection('listings').doc(this.$route.query.listingID);
            docRef.onSnapshot((doc) => {
              if (doc.exists && doc.data().transaction_status == "closed") {
                this.listingInfo.transaction_status = "closed";

                this.myBids = false;
                this.bidStatus = "Transaction Confirmed!";
                this.bidCreation = `You have confirmed the transaction for ${this.listingInfo.listing_name}!`

                var myModal = new bootstrap.Modal(this.$refs.successModal)
                var modalToggle = this.$refs.successModal;
                myModal.show(modalToggle);
              }
            }, (error) => {
              console.error('Error fetching document:', error);
            });

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
      var year = a.getFullYear().toString().substr(-2);
      var month = (a.getMonth() + 1).toString();
      var date = a.getDate().toString();
      var hour = a.getHours();
      var time = "";
      if (hour >= 12) {
        time = "pm";
        if (hour > 12) {
          hour -= 12;
        }
      } else {
        time = "am";
      }
      var min = ("0" + a.getMinutes()).slice(-2);
      var formattedDate = date + '/' + month + '/' + year + ' ' + hour + ":" + min + time;
      return formattedDate;
    },
    timeLeft(unixTimestamp) {
      const currentTimestamp = Math.floor(Date.now() / 1000);
      const timeDiff = unixTimestamp - currentTimestamp;
      if (timeDiff <= 0) {
        this.listingInfo.status = "closed";
        return "Ended";
      } else {
        const daysLeft = Math.floor(timeDiff / (24 * 3600));
        let timeRemaining = timeDiff % (24 * 3600);
        const hoursLeft = Math.floor(timeRemaining / 3600);
        timeRemaining %= 3600;
        const minutesLeft = Math.floor(timeRemaining / 60);
        const secondsLeft = timeRemaining % 60;
        const timeArr = [`${daysLeft}d`, `${hoursLeft}h`, `${minutesLeft}m`, `${secondsLeft}s`];

        var result = timeArr
        while (result && Number(result[0].slice(0, -1)) == 0) {
          result.shift();
        }
        return result.slice(0, 2).join(" ") + " left";
      }
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
      } else if (this.bidPrice < this.listingInfo.starting_bid) {
        this.bidErrMsg = `Bid price must be at least $${this.listingInfo.starting_bid}.`;
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
            this.myBids = true;
            this.bidStatus = "Bid placed!";
            this.bidCreation = `You have placed a bid of $${this.bidPrice} for ${this.listingInfo.listing_name}!`

            this.listingInfo.highest_current_bid = this.bidPrice;
            this.listingInfo.highest_current_bidder_userid = this.user.uid;

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