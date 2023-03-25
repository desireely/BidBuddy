import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import "bootstrap-icons/font/bootstrap-icons.css";
import router from "./router";
// import { auth } from "../firebaseConfig";

const app = createApp(App);
app.use(router);
app.mount("#app");

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
