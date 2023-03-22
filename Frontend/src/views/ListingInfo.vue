<template>
  <div>
    <h1>Listing Name</h1>
    <div class="container p-3">
      <div class="row my-3">
        <h4 class="mb-3">Countdown Timer here</h4>
      </div>
      <div class="row mt-2">
        <div class="col-3">
          Image here
        </div>
        <div class="col-9 border border-dark-subtle rounded">
          Product Details here
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
export default {
  name: 'ListingInfo',
  // methods: {
  //   getListingInfo() {
  //     const path = 'http://127.0.0.1:5000/listing/' + listingID;
  //     axios.get(path)
  //       .then((res) => {
  //         this.listingInfo = res.data.data.listings;
  //         console.log(res.data.data.listings);
  //       })
  //       .catch((error) => {
  //         console.error(error);
  //       });
  //   },
  // },
  // created() {
  //   this.getListingInfo();
  // },
}
</script>

<style></style>