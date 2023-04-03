<template>
  <div class="col-12 col-sm-6 col-md-4 p-2">
    <router-link
      :to="{ path: '/listinginfo', query: { listingID: listingData.listingid, username: (listingData.username ? listingData.username : currentUser) } }"
      style="text-decoration: none; color: inherit;">
      <div class="card mb-2 mycard">
        <img :src="listingData.listing_image_url" class="card-img-top img-fluid"
          style="height: 200px; object-fit: cover;">
        <div class="card-body">
          <div class="row align-items-center">
            <div class="col-7">
              <div class="d-flex align-items-center me-2">
                <h5 class="card-text text-start text-wrap">{{ listingData.listing_name }}</h5>
              </div>
            </div>
            <div class="col-5 text-end" v-if="!mylistings">
              <router-link
                :to="{ path: '/listinginfo', query: { listingID: listingData.listingid, username: (listingData.username ? listingData.username : currentUser) } }"
                class="btn btn-outline-dark py-1 px-2">Place Bid</router-link>
            </div>
          </div>
          <p class="card-text text-start text-wrap">
            <span style="color: #C6C6C6">Listed by: {{ listingData.username ? listingData.username : currentUser
            }}<br /></span>
            Auction ends on <br> {{ timeConverter(listingData.auction_end_datetime) }}
          </p>
          <hr>
          <p class="card-text m-0">Starting bid: ${{ listingData.starting_bid }}</p>
          <p class="card-text m-0">Highest bid: {{ listingData.highest_current_bid ? "$" + listingData.highest_current_bid
            : "-" }}</p>
        </div>
      </div>
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'ItemCard',
  props: {
    listingData: null,
    mylistings: {
      type: Boolean,
      default: false
    },
    currentUser: {
      type: String
    }
  },
  methods: {
    timeConverter(UNIX_timestamp) {
      var a = new Date(UNIX_timestamp * 1000);
      var year = a.getFullYear();
      var month = ("0" + (a.getMonth() + 1)).slice(-2);
      var date = ("0" + a.getDate()).slice(-2);
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
    }
  }
}
</script>

<style>
.mycard:hover {
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  transform: translateY(-5px);
  transition: all 0.2s linear;
  cursor: pointer;
}
</style>