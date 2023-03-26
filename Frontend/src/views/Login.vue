<template>
  <div>
    <h1>Login</h1>
    <div class="w-50 mx-auto">
      <form>
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
        <div class="text-end">
          <button class="btn btn-outline-dark" @click="login" v-if="email && password">Submit</button>
          <button class="btn btn-outline-secondary" disabled v-else>Submit</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { auth } from "../../firebaseConfig.js"
import router from "../router";

export default {
  name: 'Login',
  data() {
    return {
      showPassword: false,

      email: null,
      password: null,

      emailIsValid: true,
      passwordIsValid: true,

      emailErrMsg: null,
      passwordErrMsg: null,
    };
  },
  methods: {
    login() {
      event.preventDefault();
      [this.emailIsValid, this.passwordIsValid, this.emailErrMsg, this.passwordErrMsg] = [true, true, null, null];

      auth.signInWithEmailAndPassword(this.email, this.password)
        .then(function () {
          const user = auth.currentUser;
          console.log(user);

          auth.onAuthStateChanged(function (user) {
            if (user) {
              user.getIdToken().then(function (token) {
                // Use the token here
                console.log(token)
                sessionStorage.setItem('token', token);
                const userid = user.uid
                sessionStorage.setItem('userid', userid);
                console.log(userid)
                router.pushReload({ name: 'Home' });
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