<template>
  <div>
    <div class="px-4 text-center">
      <lottie-player class="w-25 mx-auto" src="https://assets9.lottiefiles.com/private_files/lf30_mn61zlcj.json"
        background="transparent" speed="1" loop autoplay></lottie-player>
      <h1 class="display-5 fw-bold">BidBuddy</h1>
      <div class="col-lg-6 mx-auto">
        <p class="lead mb-4">Make online purchasing easier and more transparent than ever with a marketplace that empowers
          users to get the best deals with our integrated bidding system.</p>
        <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
          <router-link :to="{ path: '/signup' }" class="btn btn-dark btn-lg px-4 gap-3">Get Started</router-link>
          <router-link :to="{ path: '/login' }" class="btn btn-outline-dark btn-lg px-4">Login</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Landing',
  components: {},
  props: {
  },
  data() {
    return {
    };
  },
}
</script>

<style></style>