<template>
  <div>
    <h1>Login</h1>
    <div class="w-50 mx-auto">
      <form>
        <div class="mb-3">
          <label for="email" class="form-label">Email address</label>
          <input type="email" class="form-control" id="email" v-model="email">
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input type="password" class="form-control" id="password" v-model="password">
        </div>
        <div class="text-end">
          <button class="btn btn-outline-dark" @click="login">Submit</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import {auth} from "../../firebaseConfig.js"

export default {
  name: 'Login',
  data() {
    return {
      email: null,
      password: null,
    };
  },
  methods: {
    login() {
      event.preventDefault();
      auth.signInWithEmailAndPassword(this.email, this.password)
        .then(function() {
          const user = auth.currentUser;
          console.log(user);

          auth.onAuthStateChanged(function(user) {
            if (user) {
              user.getIdToken().then(function(token) {
                // Use the token here
                console.log(token)
                sessionStorage.setItem('token', token);
                const userid = user.uid
                sessionStorage.setItem('userid', userid);
                console.log(userid)
              }).catch(function(error) {
                // Handle error here
                console.log(error.message)
              });
            }
          });
        })
        .catch(function(error) {
          console.log(error.message);
        });
    }
  }
}
</script>

<style></style>