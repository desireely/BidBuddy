<template>
  <div>
    <h1>New Listing</h1>
    <div class="container">
      <div class="row">
        <div class="col-4 my-auto">
          <div class="card">
            <img :src="listingImgURL" class="card-img-top" />
            <label for="img-upload" class="custom-file-upload">
              <br /><br /><br />{{ uploadTxt }}
            </label>
            <input id="img-upload" type="file" accept="image/*" @change="displayImg"
              :class="{ 'form-control': true, 'is-invalid': !listingImageIsValid }" ref="imgInput" />
            <div class="invalid-feedback">
              Please upload an image.
            </div>
          </div>
        </div>
        <div class="col-8">
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
            <label for="starting-date" class="form-label">Bidding Start Date</label>
            <input type="datetime-local" :class="{ 'form-control': true, 'is-invalid': !startDateIsValid }"
              v-model="startDate" class="form-control" id="starting-date" @change="validateStartDate()">
            <div class="invalid-feedback">
              {{ startDateErrMsg }}
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
              <h1 class="modal-title fs-5" id="successModalLabel">Listing created!</h1>
            </div>
            <div class="modal-body">
            </div>
            <div class="modal-footer">
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
      listingImgURL: 'https://firebasestorage.googleapis.com/v0/b/mypr-ad6b9.appspot.com/o/uploadImg.svg?alt=media&token=73f66d55-3c08-4e7f-8193-7db0dbb8a43a',
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

      startDate: null,
      startDateIsValid: true,
      startDateErrMsg: null,

      endDate: null,
      endDateIsValid: true,
      endDateErrMsg: null,
    }
  },
  methods: {
    resetInputs() {
      [this.listingImage, this.listingName, this.listingDesc, this.startingBid, this.startDate, this.endDate] = [null, null, null, null, null, null];
      [this.listingImageIsValid, this.listingNameIsValid, this.listingDescIsValid, this.startingBidIsValid, this.startDateIsValid, this.endDateIsValid] = [true, true, true, true, true, true];
      [this.listingNameErrMsg, this.listingDescErrMsg, this.startingBidErrMsg, this.startDateErrMsg, this.endDateErrMsg] = [null, null, null, null, null];
      this.listingImgURL = 'https://firebasestorage.googleapis.com/v0/b/mypr-ad6b9.appspot.com/o/uploadImg.svg?alt=media&token=73f66d55-3c08-4e7f-8193-7db0dbb8a43a';
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
          this.listingImgURL = 'https://firebasestorage.googleapis.com/v0/b/mypr-ad6b9.appspot.com/o/uploadImg.svg?alt=media&token=73f66d55-3c08-4e7f-8193-7db0dbb8a43a'
          this.listingImage = null;
          this.listingImageIsValid = false;
          this.uploadTxt = "Upload an Image";
          this.$refs.imgInput.value = null;
        }
      } else {
        this.listingImgURL = 'https://firebasestorage.googleapis.com/v0/b/mypr-ad6b9.appspot.com/o/uploadImg.svg?alt=media&token=73f66d55-3c08-4e7f-8193-7db0dbb8a43a';
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
    validateStartDate() {
      if (!this.startDate) {
        this.startDateErrMsg = "Field is required.";
        this.startDateIsValid = false;
      } else if (new Date(this.startDate) < new Date()) {
        this.startDateErrMsg = "Start date has already passed.";
        this.startDateIsValid = false;
      } else {
        this.startDateErrMsg = null;
        this.startDateIsValid = true;
      }
    },
    validateEndDate() {
      if (!this.endDate) {
        this.endDateErrMsg = "Field is required.";
        this.endDateIsValid = false;
      } else if (new Date(this.endDate) < new Date()) {
        this.endDateErrMsg = "End date has already passed.";
        this.endDateIsValid = false;
      } else if (this.startDate && this.endDate) {
        if (new Date(this.endDate) <= new Date(this.startDate)) {
          this.endDateErrMsg = "End date must be after start date.";
          this.endDateIsValid = false;
        } else {
          this.endDateErrMsg = null;
          this.endDateIsValid = true;
        }
      }
    },
    validate() {
      this.validateName();
      this.validateDesc();
      this.validateBid();
      this.validateStartDate();
      this.validateEndDate();

      if (this.listingImage) {
        this.listingImageIsValid = true;
      } else {
        this.listingImageIsValid = false;
      }

      if (this.listingImageIsValid && this.listingNameIsValid && this.listingDescIsValid && this.startingBidIsValid && this.startDateIsValid && this.endDateIsValid) {
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
          auction_start_datetime: this.startDate,
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

        axios.post('http://127.0.0.1:5000/listing', { data: listing })
          .then(response => {
            console.log(response.data)
            this.resetInputs();
            var myModal = new bootstrap.Modal(this.$refs.successModal)
            var modalToggle = this.$refs.successModal;
            myModal.show(modalToggle);
          })
          .catch(error => {
            console.log(error)
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