<script setup>
</script>

<style></style>

<template>
  <div>
    <div class="offcanvas offcanvas-start" tabindex="-1" id="offcanvasNavbar" aria-labelledby="offcanvasNavbarLabel">
      <div class="border-end min-vh-100 px-3">
        <div class="py-3">
          <h3 class="d-flex position-relative align-items-center p-1 text-dark text-decoration-none text-center">
            BidBuddy <button type="button" class="btn-close position-absolute" style="right:0;top:0;font-size:0.7em"
              data-bs-dismiss="offcanvas" aria-label="Close"></button>
          </h3>
          <div class="input-group p-1 mb-1">
            <span class="input-group-text bg-white border border-end-0" id="search">
              <i class="bi bi-search"></i>
            </span>
            <input type="text" class="form-control border border-start-0" placeholder="Search" aria-label="Search"
              aria-describedby="search" v-model="searchInput">
          </div>
          <!-- Navigation links in sidebar-->
          <ul class="nav nav-pills flex-column mb-auto">
            <li class="nav-item">
              <router-link to="/" class="nav-link text-dark" active-class="bg-dark text-white">
                <i class="bi bi-house me-2" width="16" height="16"></i>
                Home
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/mylistings" class="nav-link text-dark" active-class="bg-dark text-white">
                <i class="bi bi-bag me-2" width="16" height="16"></i>
                My Listings
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/mybids" class="nav-link text-dark" active-class="bg-dark text-white">
                <i class="bi bi-coin me-2" width="16" height="16"></i>
                My Bids
              </router-link>
            </li>
            <li class="nav-item pb-2" style="position:fixed; bottom:0;">
              <button class="nav-link text-dark" active-class="bg-dark text-white" @click="logout">
                <i class="bi bi-box-arrow-right me-2" width="16" height="16"></i>
                Log Out
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="container-fluid h-100 d-flex flex-column">
      <!-- h-100 takes the full height of the container-->
      <div class="row h-100">
        <div class="col-2 border-end min-vh-100 px-3 d-none d-lg-block" v-if="user">
          <div class="sticky-top py-3">
            <h3 class="d-flex align-items-center p-1 text-dark text-decoration-none text-center">
              BidBuddy</h3>
            <!-- Navigation links in sidebar-->
            <ul class="nav nav-pills flex-column mb-auto">
              <li class="nav-item">
                <router-link to="/" class="nav-link text-dark" active-class="bg-dark text-white">
                  <i class="bi bi-house me-2" width="16" height="16"></i>
                  Home
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/mylistings" class="nav-link text-dark" active-class="bg-dark text-white">
                  <i class="bi bi-bag me-2" width="16" height="16"></i>
                  My Listings
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/mybids" class="nav-link text-dark" active-class="bg-dark text-white">
                  <i class="bi bi-coin me-2" width="16" height="16"></i>
                  My Bids
                </router-link>
              </li>
              <li class="nav-item pb-2" style="position:fixed; bottom:0;">
                <button class="nav-link text-dark" active-class="bg-dark text-white" @click="logout">
                  <i class="bi bi-box-arrow-right me-2" width="16" height="16"></i>
                  Log Out
                </button>
              </li>
            </ul>
          </div>
        </div>
        <div :class="{ 'col': user, 'p-0': true }">
          <!-- Top navbar -->
          <div class="container-fluid p-0 border-bottom sticky-top bg-white">
            <nav class="navbar navbar-expand-lg">
              <router-link to="/landing" v-if="!user" class="col-3" style="text-decoration: none; color: inherit;">
                <h3 class="d-flex align-items-center p-1 text-dark text-decoration-none text-center ms-3">
                  BidBuddy</h3>
              </router-link>
              <div v-if="user" class="col-2 col-sm-4 ms-3 d-flex align-items-center">
                <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasNavbar"
                  aria-controls="offcanvasNavbar">
                  <span class="navbar-toggler-icon"></span>
                </button>
                <div class="input-group p-1 mx-3 d-none d-sm-flex">
                  <span class="input-group-text bg-white border border-end-0" id="search">
                    <i class="bi bi-search"></i>
                  </span>
                  <input type="text" class="form-control border border-start-0" placeholder="Search" aria-label="Search"
                    aria-describedby="search" v-model="searchInput">
                </div>
              </div>
              <div class="col d-flex justify-content-end me-3">
                <router-link to="/newlisting" class="btn btn-dark mx-2 px-3 py-2" v-if="user">
                  Create a listing
                </router-link>
                <router-link to="/signup" class="text-decoration-none text-dark px-3 py-2" v-if="!user">
                  Sign Up
                </router-link>
                <router-link to="/login" class="text-decoration-none text-dark pe-3 py-2" v-if="!user">
                  Login
                </router-link>
                <!-- icon for profile if logged in -->
                <i class="bi bi-person-circle mx-3" style="font-size: 30px" v-if="user"></i>
                <span class="d-flex align-self-center me-3" v-if="user">Hi, {{ username }}</span>
              </div>
            </nav>
          </div>
          <!-- Contains the main content of the webpage-->
          <p style="padding: 20px; text-align: justify;">
            <router-view :user="user" :username="username" :token="token" :searchInput="searchInput"></router-view>
          </p>

        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { auth } from "../firebaseConfig.js"
import router from "./router";
import axios from 'axios';

export default {
  data() {
    return {
      user: null,
      token: null,
      searchInput: null,
      username: null,
    }
  },
  created() {
    const self = this;
    auth.onAuthStateChanged(function (user) {
      if (user) {
        user.getIdToken().then(function (token) {
          // Use the token here
          self.token = token;
          self.user = user;
          self.getUsername();
        }).catch(function (error) {
          // Handle error here
          console.log(error.message)
        });
      }
    });
  },
  methods: {
    getUsername() {
      axios.get(`${this.$user}/${this.user.uid}`)
        .then((res) => {
          console.log(res.data);
          this.username = res.data.data.username;
        })
        .catch((error) => {
          console.error(error);
          this.emailIsValid = false;
          this.emailErrMsg = "Email is already registered."
        });
    },
    logout() {
      const self = this;
      auth.signOut()
        .then(function () {
          console.log("Logged Out")
          self.token = null;
          self.user = null;
          router.pushReload({ name: 'Landing' });
        })
        .catch(function (error) {
          console.log(error.message)
        })
    }
  }
}
</script>