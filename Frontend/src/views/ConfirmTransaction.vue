<template>
  <div>
    <div class="container-fluid">
      <div class="row align-items-center justify-content-center" style="height: calc(100vh - 200px); overflow: hidden;">
        <div class="col text-center">
          <h1 class="flashy">{{ transactionMsg[0] }}</h1>
          <p class="fs-5">{{ transactionMsg[1] }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import router from "../router";

export default {
  name: 'ConfirmTransaction',
  props: {
    user: Object,
    token: String
  },
  data() {
    return {
      transactionMsg: "",
    }
  },
  created() {
    this.confirmTransaction();
  },
  methods: {
    confirmTransaction() {
      const info = {
        user_id: this.user.uid,
        data: this.$route.query.data
      }
      axios.post(this.$confirmTransaction, info)
        .then(response => {
          console.log(response.data)
          this.transactionMsg = ["Transaction confirmed!", "Redirecting to home page..."]
          setTimeout(() => {
            router.push('/')
          }, 3000);
        })
        .catch(error => {
          console.log(error)
          this.transactionMsg = ["Oops!", "Failed to confirm transaction."]
        })
    },
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka+One&display=swap');

.flashy {
  font-family: 'Fredoka One', sans-serif;
  font-weight: bold;
}
</style>