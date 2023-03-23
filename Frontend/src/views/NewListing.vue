<template>
  <div>
    <h1>New Listing</h1>
    <div class="container">
      <form>
        <div class="row">
          <div class="col-4 mb-3">
            <div class="card">
              <img :src="listingImgURL" class="card-img-top"/>
              <label for="img-upload" class="custom-file-upload">
                <br/><br/><br/>{{uploadTxt}}
              </label>
              <input id="img-upload" type="file" accept="image/*" @change="displayImg"/>
            </div>
          </div>
          <div class="col-8">
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
          </div>
          <div class="text-end">
            <button type="submit" class="btn btn-outline-dark">Create</button>
          </div>
        </div>
      </form>
    </div>

  </div>
</template>

<script>
export default {
  name: 'NewListing',
  data() {
    return {
      listingImgURL: 'https://firebasestorage.googleapis.com/v0/b/mypr-ad6b9.appspot.com/o/uploadImg.svg?alt=media&token=73f66d55-3c08-4e7f-8193-7db0dbb8a43a',
      uploadTxt: "Upload an Image",
    }
  },
  methods: {
    displayImg(event) {
      var img = event.target.files[0];
      if (img.type.startsWith('image/')) {
        this.listingImgURL = URL.createObjectURL(img);
        if (this.listingImgURL == 'https://firebasestorage.googleapis.com/v0/b/mypr-ad6b9.appspot.com/o/uploadImg.svg?alt=media&token=73f66d55-3c08-4e7f-8193-7db0dbb8a43a') {
          this.uploadTxt = "Upload an Image";
        } else {
          this.uploadTxt = "";
        }
      } else {
          this.listingImgURL = 'https://firebasestorage.googleapis.com/v0/b/mypr-ad6b9.appspot.com/o/uploadImg.svg?alt=media&token=73f66d55-3c08-4e7f-8193-7db0dbb8a43a'
          this.uploadTxt = "Please upload an image file!";
      }
    }
  }
}
</script>

<style>
  input[type="file"] {
    display: none;
  }
  .custom-file-upload {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
  }
</style>