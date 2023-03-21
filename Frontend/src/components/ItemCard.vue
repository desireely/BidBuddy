<template>
  <div class="card" style="width: 20rem;">
    <img src="..." class="card-img-top">
    <div class="card-body">
      <div class="row">
        <div class="col">
          <h5 class="card-text">Listing Name</h5>
        </div>
        <div class="col text-end">
          <router-link to="/listinginfo" class="btn btn-outline-dark py-1 px-2">Place Bid</router-link>
        </div>
      </div>
      <h5 class="card-title">Time Left <span style="font-weight: normal; color: #C6C6C6">(date)</span> </h5>
      <hr>
      <p class="card-text m-0">Start Price:</p>
      <p class="card-text m-0">Current highest bid: $</p>
      <p class="card-text m-0">Number of bidders:</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ItemCard'
}
</script>

<style></style>