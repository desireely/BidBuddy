<template>
  <div>
    <h1>Sign Up</h1>
    <div class="w-50 mx-auto">
      <div class="mb-3">
        <label for="email" class="form-label">Email address</label>
        <input type="email" :class="{ 'form-control': true, 'is-invalid': !emailIsValid }" id="email" v-model="email" @change="validateEmail">
        <div class="invalid-feedback">
          {{ emailErrMsg }}
        </div>
      </div>
      <div class="mb-3">
        <label for="username" class="form-label">Username</label>
        <input type="text" class="form-control" id="username" v-model="username">
      </div>
      <div class="mb-3">
        <label for="teleuser" class="form-label">Telegram Username</label>
        <input type="text" class="form-control" id="teleuser" v-model="teleuser">
      </div>
      <label for="password" class="form-label">Password</label>
      <div class="input-group mb-3">
        <input :type="showPassword ? 'text' : 'password'" :class="{ 'form-control': true, 'is-invalid': !passwordIsValid }" id="password" v-model="password" @change="validatePassword">
        <div class="input-group-append">
          <button class="input-group-text" type="button" id="togglePassword" @click="showPassword = !showPassword">
            <i v-bind:class="[showPassword ? 'bi-eye-fill' : 'bi-eye-slash-fill']"></i>
          </button>
        </div>
        <div class="invalid-feedback">
          Password must contain at least 6 characters.
        </div>
      </div>
      <div class="text-end">
        <button class="btn btn-outline-dark" @click="validate" v-if="email && username && teleuser && password">Submit</button>
        <button class="btn btn-outline-secondary" disabled v-else>Submit</button>
      </div>
    </div>
  </div>
</template>

<script>
import { auth } from "../../firebaseConfig.js"
import router from "../router";
import axios from 'axios';
export default {
  name: 'Signup',
  data() {
    return {
      email: '',
      username: '',
      teleuser: '',
      password: '',

      emailIsValid: true,
      passwordIsValid: true,

      emailErrMsg: '',
      showPassword: false,
    };
  },
  methods: {
    validateEmail() {
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      this.emailIsValid = emailRegex.test(this.email);
      if (this.emailIsValid) {
        this.emailErrMsg = "";
      } else {
        this.emailErrMsg = "Invalid email format.";
      }
    },
    validatePassword() {
      if (this.password.length >= 6) {
        this.passwordIsValid = true;
      } else {
        this.passwordIsValid = false;
      }
    },
    validate() {
      this.validateEmail();
      this.validatePassword();
      if (this.emailIsValid && this.passwordIsValid) {
        this.registerUser();
      }
    },
    registerUser() {
      const userInfo = {
        email: this.email,
        password: this.password,
        teleuser: this.teleuser,
        username: this.username
      }
      console.log(userInfo)
      
      axios.post(this.$user, userInfo)
        .then((res) => {
          console.log(res);
          this.login();
        })
        .catch((error) => {
          console.error(error);
          this.emailIsValid = false;
          this.emailErrMsg = "Email is already registered."
        });
    },
    login() {
      const self = this;
      auth.signInWithEmailAndPassword(this.email, this.password)
        .then(function () {
          const user = auth.currentUser;
          console.log(user);

          auth.onAuthStateChanged(function (user) {
            if (user) {
              user.getIdToken().then(function (token) {
                router.pushReload({ name: 'Home' });
              }).catch(function (error) {
                console.log(error.message)
              });
            }
          });
        })
        .catch((error) => {
          console.log(errorMessage);
        });
    }
  },
}
</script>

<style></style>