import { createRouter, createWebHistory } from "vue-router";

import Home from "../views/Home.vue";
import MyListings from "../views/MyListings.vue";
import MyBids from "../views/MyBids.vue";
import NewListing from "../views/NewListing.vue";
import SignUp from "../views/SignUp.vue";
import Login from "../views/Login.vue";
import ListingInfo from "../views/ListingInfo.vue";

const router = createRouter({
  scrollBehavior(to, from, savedPosition) {
    // always scroll to top
    return { top: 0 };
  },
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Home",
      component: Home,
    },
    {
      path: "/mylistings",
      name: "My Listings",
      component: MyListings,
    },
    {
      path: "/mybids",
      name: "My Bids",
      component: MyBids,
    },
    {
      path: "/newlisting",
      name: "New Listing",
      component: NewListing,
    },
    {
      path: "/signup",
      name: "Sign Up",
      component: SignUp,
    },
    {
      path: "/login",
      name: "Login",
      component: Login,
    },
    {
      path: "/listinginfo",
      name: "Listing Info",
      component: ListingInfo,
    },
  ],
});

export default router;
