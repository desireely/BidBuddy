import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import "bootstrap-icons/font/bootstrap-icons.css";
import router from "./router";
// import { auth } from "../firebaseConfig";

const app = createApp(App);
app.use(router);
app.mount("#app");

// Global Variables
app.config.globalProperties.$listing = "http://127.0.0.1:5007/listing";
app.config.globalProperties.$user = "http://127.0.0.1:5005/user";
app.config.globalProperties.$qrCode = "http://127.0.0.1:5009/qrcode";
app.config.globalProperties.$showListing = "http://127.0.0.1:5006/showlisting";
app.config.globalProperties.$createListing = "http://127.0.0.1:5001/createlisting";
app.config.globalProperties.$showDetailsOfBids = "http://127.0.0.1:5002/showdetailsofbids";
app.config.globalProperties.$bidForListing = "http://127.0.0.1:5015/bidforlisting";
app.config.globalProperties.$confirmTransaction = "http://127.0.0.1:5009/confirmtransaction";

// let app;
// auth.onAuthStateChanged(() => {
//   if (!app) {
//     app = new Vue({
//       router,
//       store,
//       render: (h) => h(App),
//     }).$mount("#app");
//   }
//   if (user) {
//     user
//       .getIdToken()
//       .then(function (token) {
//         // Use the token here
//         console.log(token);
//         sessionStorage.setItem("token", token);
//         userid = user.uid;
//         sessionStorage.setItem("userid", userid);
//         console.log(userid);
//       })
//       .catch(function (error) {
//         // Handle error here
//         console.log(error.message);
//       });
//   }
// });
