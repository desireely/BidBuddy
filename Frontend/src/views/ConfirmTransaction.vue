<template>
  <div>
    <div class="container-fluid d-flex justify-content-center align-items-center"
      style="height: calc(100vh - 200px); overflow: hidden;">
      <p class="fs-5">{{ transactionMsg }}</p>
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
          this.transactionMsg = "Transaction confirmed successfully! Redirecting to home page..."
          setTimeout(() => {
            router.push('/')
          }, 3000);
        })
        .catch(error => {
          console.log(error)
          this.transactionMsg = "Failed to confirm transaction."
        })
    },
  }
}
</script>

<style></style>