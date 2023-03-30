<template>
  <div>
    <h1>Sign Up</h1>
    <div class="w-50 mx-auto">
      <form>
        <div class="mb-3">
          <label for="email" class="form-label">Email address</label>
          <input type="email" class="form-control" id="email" v-model="email">
        </div>
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input type="text" class="form-control" id="username" v-model="username">
        </div>
        <div class="mb-3">
          <label for="teleuser" class="form-label">Telegram Username</label>
          <input type="text" class="form-control" id="teleuser" v-model="teleuser">
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input type="password" class="form-control" id="password" v-model="password">
        </div>
        <div class="text-end">
          <button type="submit" class="btn btn-outline-dark" @click="registerUser">Submit</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'Signup',
  data() {
    return {
      email: '',
      username: '',
      teleuser: '',
      password: '',
    };
  },
  methods: {
    registerUser() {
      event.preventDefault();
      axios.post(this.$user, { email: this.email, password: this.password, teleuser: this.teleuser, username: this.username })
        .then((res) => {
          console.log(res);
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
}
</script>

<style></style>