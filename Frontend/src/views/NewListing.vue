<template>
  <div>
    <h1>New Listing</h1>
    <div class="container">
      <div class="row">
        <div class="col-4 text-center my-auto">
          upload pic function here
        </div>
        <div class="col-8">
          <form>
            <div class="mb-3">
              <label for="listing-name" class="form-label">Listing Name</label>
              <input type="text" class="form-control" id="listing-name">
            </div>
            <div class="mb-3">
              <label for="listing-description" class="form-label">Listing Decription</label>
              <textarea class="form-control" id="listing-description"></textarea>
            </div>
            <div class="input-group mb-3">
              <span class="input-group-text" id="basic-addon1">$</span>
              <input type="number" min="0" class="form-control" placeholder="Starting Bid">
            </div>
            <div class="mb-3">
              <label for="starting-date" class="form-label">Bidding Start Date</label>
              <input type="datetime-local" class="form-control" id="starting-date">
            </div>
            <div class="mb-3">
              <label for="ending-date" class="form-label">Bidding End Date</label>
              <input type="datetime-local" class="form-control" id="ending-date">
            </div>
            <div class="text-end">
              <button type="submit" class="btn btn-outline-dark">Create</button>
            </div>
          </form>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'NewListing'
}
</script>

<style></style>