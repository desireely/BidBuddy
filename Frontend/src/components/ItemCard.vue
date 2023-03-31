<template>
  <div class="col-12 col-sm-6 col-md-4 p-2">
    <div class="card mb-2">
      <img src="" class="card-img-top">
      <div class="card-body">
        <div class="row align-items-center">
          <div class="col-7">
            <div class="d-flex align-items-center me-2">
              <h5 class="card-text text-start text-wrap">{{ listingData.listing_name }}</h5>
            </div>
          </div>
          <div class="col-5 text-end">
            <router-link :to="{ path: '/listinginfo', query: { listingID: listingData.listingid } }"
              class="btn btn-outline-dark py-1 px-2">Place Bid</router-link>
          </div>
        </div>
        <p class="card-text text-start text-wrap mt-2" style="color: #C6C6C6">Auction ends on <br> {{
          timeConverter(listingData.auction_end_datetime)
        }}</p>
        <hr>
        <p class="card-text m-0">Start Price: ${{ listingData.starting_bid }}</p>
        <p class="card-text m-0">Current highest bid: ${{ listingData.highest_current_bid }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ItemCard',
  props: {
    listingData: null,
  },
  methods: {
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