<template>
  <div class="d-flex justify-content-center align-items-center" style="height: calc(100vh - 200px); overflow: hidden;">
    <div class="card w-50 mx-auto p-3">
      <div class="card-body">
        <h1 class="card-title text-center">Login</h1>
        <div class="mb-3">
          <label for="email" class="form-label">Email address</label>
          <input type="email" :class="{ 'form-control': true, 'is-invalid': !emailIsValid }" id="email" v-model="email">
          <div class="invalid-feedback">
            {{ emailErrMsg }}
          </div>
        </div>
        <label for="password" class="form-label">Password</label>
        <div class="input-group mb-3">
          <input :type="showPassword ? 'text' : 'password'"
            :class="{ 'form-control': true, 'is-invalid': !passwordIsValid }" id="password" v-model="password">
          <div class="input-group-append">
            <button class="input-group-text" type="button" id="togglePassword" @click="showPassword = !showPassword">
              <i v-bind:class="[showPassword ? 'bi-eye-fill' : 'bi-eye-slash-fill']"></i>
            </button>
          </div>
          <div class="invalid-feedback">
            {{ passwordErrMsg }}
          </div>
        </div>
        <div class="d-flex justify-content-center">
          <button class="btn btn-dark w-100" @click="login" v-if="email && password">Login</button>
          <button class="btn btn-dark w-100" style="background-color:#000000" disabled v-else>Login</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { auth } from "../../firebaseConfig.js"
import router from "../router";

export default {
  name: 'Login',
  props: {
    user: Object,
    token: String
  },
  data() {
    return {
      showPassword: false,

      email: null,
      password: null,

      emailIsValid: true,
      passwordIsValid: true,

      emailErrMsg: null,
      passwordErrMsg: null,

      redirect: null,
    };
  },
  created() {
    if (this.$route.query.listingID && this.$route.query.data) {
      this.redirect = {
        path: '/confirmtransaction',
        query: { listingID: this.$route.query.listingID, data: this.$route.query.data }
      }
    } else {
      this.redirect = '/'
    }
  },
  methods: {
    login() {
      [this.emailIsValid, this.passwordIsValid, this.emailErrMsg, this.passwordErrMsg] = [true, true, null, null];

      const self = this;
      auth.signInWithEmailAndPassword(this.email, this.password)
        .then(function () {
          const user = auth.currentUser;
          console.log(user);

          auth.onAuthStateChanged(function (user) {
            if (user) {
              user.getIdToken().then(function (token) {
                // Use the token here
                console.log(self.user.uid)
                router.pushReload(self.redirect);
              }).catch(function (error) {
                // Handle error here
                console.log(error.message)
              });
            }
          });
        })
        .catch((error) => {
          const errorCode = error.code;
          const errorMessage = error.message;

          switch (errorCode) {
            case 'auth/invalid-email':
              this.emailErrMsg = "Invalid email format.";
              this.emailIsValid = false;
              break;
            case 'auth/user-not-found':
              this.emailErrMsg = "We couldn't find an account with that email.";
              this.emailIsValid = false;
              break;
            case 'auth/wrong-password':
              this.passwordErrMsg = "Your account or password is incorrect.";
              this.passwordIsValid = false;
              break;
            // Handle other error codes as needed
            default:
              console.log(errorMessage);
          }
        });
    }
  }
}
</script>

<style></style>