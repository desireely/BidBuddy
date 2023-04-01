<template>
  <div>
    <h1>New Listing</h1>
    <div class="container">
      <div class="row">
        <div class="col-12 col-md-4 my-auto py-3">
          <div class="card">
            <img :src="listingImgURL" class="card-img-top" />
            <label for="img-upload" class="custom-file-upload d-flex align-items-end pb-5 pb-md-4 pb-xl-5">
              {{ uploadTxt }}
            </label>
            <input id="img-upload" type="file" accept="image/*" @change="displayImg"
              :class="{ 'form-control': true, 'is-invalid': !listingImageIsValid }" ref="imgInput" />
            <div class="invalid-feedback">
              Please upload an image.
            </div>
          </div>
        </div>
        <div class="col-12 col-md-8">
          <div class="mb-3">
            <label for="listing-name" class="form-label">Listing Name</label>
            <input type="text" :class="{ 'form-control': true, 'is-invalid': !listingNameIsValid }" v-model="listingName"
              id="listing-name" @change="validateName()">
            <div class="invalid-feedback">
              {{ listingNameErrMsg }}
            </div>
          </div>
          <div class="mb-3">
            <label for="listing-description" class="form-label">Listing Decription</label>
            <textarea :class="{ 'form-control': true, 'is-invalid': !listingDescIsValid }" v-model="listingDesc"
              id="listing-description" @change="validateDesc()"></textarea>
            <div class="invalid-feedback">
              {{ listingDescErrMsg }}
            </div>
          </div>
          <div class="input-group mb-3">
            <span class="input-group-text" id="basic-addon1">$</span>
            <input type="number" min="0" :class="{ 'form-control': true, 'is-invalid': !startingBidIsValid }"
              v-model="startingBid" placeholder="Starting Bid" @change="validateBid()">
            <div class="invalid-feedback">
              {{ startingBidErrMsg }}
            </div>
          </div>
          <div class="mb-3">
            <label for="ending-date" class="form-label">Bidding End Date</label>
            <input type="datetime-local" :class="{ 'form-control': true, 'is-invalid': !endDateIsValid }"
              v-model="endDate" id="ending-date" @change="validateEndDate()">
            <div class="invalid-feedback">
              {{ endDateErrMsg }}
            </div>
          </div>
        </div>
        <div class="text-end">
          <button @click="validate()" class="btn btn-outline-dark">Create</button>
        </div>
      </div>

      <div class="modal fade" id="successModal" tabindex="-1" aria-labelledby="successModalLabel" aria-hidden="true"
        ref="successModal">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h1 class="modal-title fs-5" id="successModalLabel">{{ listingStatus }}</h1>
            </div>
            <div class="modal-body">
              {{ listingCreation }}
            </div>
            <div class="modal-footer">
              <router-link to="/mylistings">
                <button type="button" class="btn btn-outline-dark" data-bs-dismiss="modal">My Listings</button>
              </router-link>
              <button type="button" class="btn btn-dark" data-bs-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'NewListing',
  props: {
    user: Object,
    token: String
  },
  data() {
    return {
      listingStatus: null,
      listingCreation: null,

      listingImgURL: 'https://i.pinimg.com/originals/82/50/eb/8250ebbe710fdc11dc3332e02ad7cf42.jpg',
      uploadTxt: "Upload an Image",
      listingImage: null,
      listingImageIsValid: true,

      listingName: null,
      listingNameIsValid: true,
      listingNameErrMsg: null,

      listingDesc: null,
      listingDescIsValid: true,
      listingDescErrMsg: null,

      startingBid: null,
      startingBidIsValid: true,
      startingBidErrMsg: null,

      endDate: null,
      endDateIsValid: true,
      endDateErrMsg: null,
    }
  },
  methods: {
    resetInputs() {
      [this.listingImage, this.listingName, this.listingDesc, this.startingBid, this.endDate] = [null, null, null, null, null];
      [this.listingImageIsValid, this.listingNameIsValid, this.listingDescIsValid, this.startingBidIsValid, this.endDateIsValid] = [true, true, true, true, true];
      [this.listingNameErrMsg, this.listingDescErrMsg, this.startingBidErrMsg, this.endDateErrMsg] = [null, null, null, null];
      this.listingImgURL = 'https://i.pinimg.com/originals/82/50/eb/8250ebbe710fdc11dc3332e02ad7cf42.jpg';
      this.uploadTxt = "Upload an Image";
      this.$refs.imgInput.value = null;
    },
    displayImg(event) {
      if (event.target.files[0]) {
        if (event.target.files[0].type.startsWith('image/')) {
          this.listingImage = event.target.files[0];
          this.listingImgURL = URL.createObjectURL(this.listingImage);
          this.uploadTxt = "";
          this.listingImageIsValid = true;
        } else {
          this.listingImgURL = 'https://i.pinimg.com/originals/82/50/eb/8250ebbe710fdc11dc3332e02ad7cf42.jpg'
          this.listingImage = null;
          this.listingImageIsValid = false;
          this.uploadTxt = "Upload an Image";
          this.$refs.imgInput.value = null;
        }
      } else {
        this.listingImgURL = 'https://i.pinimg.com/originals/82/50/eb/8250ebbe710fdc11dc3332e02ad7cf42.jpg';
        this.listingImage = null;
        this.listingImageIsValid = false;
        this.uploadTxt = "Upload an Image";
        this.$refs.imgInput.value = null;
      }
    },
    validateName() {
      if (!this.listingName) {
        this.listingNameErrMsg = "Field is required.";
        this.listingNameIsValid = false;
      } else {
        this.listingNameErrMsg = null;
        this.listingNameIsValid = true;
      }
    },
    validateDesc() {
      if (!this.listingDesc) {
        this.listingDescErrMsg = "Field is required.";
        this.listingDescIsValid = false;
      } else {
        this.listingDescErrMsg = null;
        this.listingDescIsValid = true;
      }
    },
    validateBid() {
      if (String(this.startingBid) == "0") {
        this.startingBidErrMsg = null;
        this.startingBidIsValid = true;
      } else if (!this.startingBid) {
        this.startingBidErrMsg = "Field is required.";
        this.startingBidIsValid = false;
      } else if (isNaN(this.startingBid) || this.startingBid < 0) {
        this.startingBidErrMsg = "Please enter a valid starting bid.";
        this.startingBidIsValid = false;
      } else {
        this.startingBidErrMsg = null;
        this.startingBidIsValid = true;
      }
    },
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
      }
    },
    validate() {
      this.validateName();
      this.validateDesc();
      this.validateBid();
      this.validateEndDate();

      if (this.listingImage) {
        this.listingImageIsValid = true;
      } else {
        this.listingImageIsValid = false;
      }

      if (this.listingImageIsValid && this.listingNameIsValid && this.listingDescIsValid && this.startingBidIsValid && this.endDateIsValid) {
        this.newListing();
      }
    },
    newListing() {
      var reader = new FileReader();
      reader.readAsDataURL(this.listingImage);
      reader.onload = () => {
        var base64String = reader.result.replace('data:', '').replace(/^.+,/, '');

        var listing = {
          userid: this.user.uid,
          auction_end_datetime: this.endDate,
          listing_description: this.listingDesc,
          listing_image: {
            name: this.listingImage.name,
            type: this.listingImage.type,
            image: base64String
          },
          listing_name: this.listingName,
          starting_bid: Number(this.startingBid)
        };
        console.log(listing)

        axios.post(this.$createListing, listing)
          .then(response => {
            console.log(response.data)
            this.listingStatus = "Listing created!";
            this.listingCreation = `You've created a new listing for ${this.listingName}!`
            this.resetInputs();
            var myModal = new bootstrap.Modal(this.$refs.successModal)
            var modalToggle = this.$refs.successModal;
            myModal.show(modalToggle);
          })
          .catch(error => {
            console.log(error);
            this.listingStatus = "Listing was not created!";
            this.listingCreation = "There was an error creating your listing."
            var myModal = new bootstrap.Modal(this.$refs.successModal)
            var modalToggle = this.$refs.successModal;
            myModal.show(modalToggle);
          });
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