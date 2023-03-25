<script setup>
</script>

<style></style>

<template>
  <div>
    <div class="container-fluid h-100 d-flex flex-column">
      <!-- h-100 takes the full height of the container-->
      <div class="row h-100">
        <div class="col-2 border-end min-vh-100 p-3" v-if="userID">
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
            <li>
              <router-link to="/mylistings" class="nav-link text-dark" active-class="bg-dark text-white">
                <i class="bi bi-bag me-2" width="16" height="16"></i>
                My Listings
              </router-link>
            </li>
            <li>
              <router-link to="/mybids" class="nav-link text-dark" active-class="bg-dark text-white">
                <i class="bi bi-coin me-2" width="16" height="16"></i>
                My Bids
              </router-link>
            </li>
            <li>
              <button class="nav-link text-dark" active-class="bg-dark text-white" @click="logout">
                <i class="bi bi-box-arrow-right me-2" width="16" height="16"></i>
                Log Out
              </button>
            </li>
          </ul>
        </div>
        <div :class="{'col-10': userID, 'p-0': true}">
          <!-- Top navbar -->
          <div class="container-fluid p-0 border-bottom">
            <nav class="navbar navbar-expand-lg">
              <div class="col-3">
                <div class="input-group p-1 mx-3">
                  <span class="input-group-text bg-white border border-end-0" id="search">
                    <i class="bi bi-search"></i>
                  </span>
                  <input type="text" class="form-control border border-start-0" placeholder="Search" aria-label="Search"
                    aria-describedby="search">
                </div>
              </div>
              <div class="col-9 d-flex justify-content-end">
                <router-link to="/newlisting" class="btn btn-dark mx-2 px-3 py-2" v-if="userID">
                  Create a listing
                </router-link>
                <router-link to="/signup" class="text-decoration-none text-dark px-3 py-2" v-if="!userID">
                  Sign Up
                </router-link>
                <router-link to="/login" class="text-decoration-none text-dark pe-3 py-2" v-if="!userID">
                  Login
                </router-link>
                <!-- icon for profile if logged in -->
                <i class="bi bi-person-circle ms-3 me-4" style="font-size: 30px" v-if="userID"></i>
              </div>
            </nav>
          </div>
          <!-- Contains the main content of the webpage-->
          <p style="padding: 20px; text-align: justify;">
            <router-view />
          </p>

        </div>
      </div>
    </div>
  </div>
</template>


<script>
  import { auth } from "../firebaseConfig.js"
  import router from "./router";

  export default {
    computed: {
      userID() {
        return !!sessionStorage.getItem('userid')
      }
    },
    methods: {
      logout() {
        auth.signOut()
        .then(function(){
          console.log("Logged Out")
          sessionStorage.clear();
          router.pushReload({ name: 'Login' });
        })
        .catch(function(error){
          console.log(error.message)
        })
      }
    }
  }
</script>
