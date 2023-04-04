import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import "bootstrap-icons/font/bootstrap-icons.css";
import router from "./router";
import "@lottiefiles/lottie-player";
import { library } from "@fortawesome/fontawesome-svg-core";
import { fas } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

const app = createApp(App);
app.use(router);
app.mount("#app");
library.add(fas);
app.component("font-awesome-icon", FontAwesomeIcon);

// Global Variables
app.config.globalProperties.$listing = "http://127.0.0.1:5007/listing";
app.config.globalProperties.$user = "http://127.0.0.1:5005/user";
app.config.globalProperties.$qrCode = "http://127.0.0.1:5009/qrcode";
app.config.globalProperties.$showListing = "http://127.0.0.1:5006/showlisting";
app.config.globalProperties.$createListing =
  "http://127.0.0.1:5001/createlisting";
app.config.globalProperties.$showDetailsOfBids =
  "http://127.0.0.1:5002/showdetailsofbids";
app.config.globalProperties.$bidForListing =
  "http://127.0.0.1:5015/bidforlisting";
app.config.globalProperties.$confirmTransaction =
  "http://127.0.0.1:5008/confirmtransaction";
app.config.globalProperties.$reopenlisting =
  "http://127.0.0.1:5010/reopenlisting";
app.config.globalProperties.$deletelisting =
  "http://127.0.0.1:5025/deletelisting";
