<template>
  <div class="col-12 col-sm-6 col-md-4 p-2">
    <router-link
      :to="{ path: '/listinginfo', query: { listingID: listingData.listingid, username: (listingData.username ? listingData.username : currentUser) } }"
      style="text-decoration: none; color: inherit;">
      <div class="card mb-2 h-100 mycard">
        <img :src="listingData.listing_image_url" class="card-img-top img-fluid"
          style="height: 200px; object-fit: cover;">
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-black border border-light rounded-circle"
          v-if="listingData.highest_current_bidder_userid && listingData.highest_current_bidder_userid == uid">
          <font-awesome-icon :icon="['fas', 'crown']" style="color: #ffffff;" />
        </span>
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
                class="btn btn-outline-dark py-1 px-2" v-if="listingData.userid != uid">Place Bid</router-link>
            </div>
          </div>
          <p class="card-text text-start text-wrap">
            <span style="color: #C6C6C6">Listed by: {{ listingData.username ? listingData.username : currentUser
            }}<br /></span>
            {{ timeLeft(listingData.auction_end_datetime) }} ({{ timeConverter(listingData.auction_end_datetime) }})
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
    },
    uid: {
      type: String
    }
  },
  mounted() {
    setInterval(() => {
      this.$forceUpdate();
    }, 1000);
  },
  methods: {
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