import { createRouter, createWebHistory } from "vue-router";

import Home from "../views/Home.vue";
import MyListings from "../views/MyListings.vue";
import MyBids from "../views/MyBids.vue";
import NewListing from "../views/NewListing.vue";
import SignUp from "../views/SignUp.vue";
import Login from "../views/Login.vue";
import ListingInfo from "../views/ListingInfo.vue";
import NoResults from "../views/NoResults.vue";
import ConfirmTransaction from "../views/ConfirmTransaction.vue";
import Landing from "../views/Landing.vue";

import { auth } from "../../firebaseConfig.js";

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
      beforeEnter: guardMyroute,
    },
    {
      path: "/mylistings",
      name: "My Listings",
      component: MyListings,
      beforeEnter: guardMyroute,
    },
    {
      path: "/mybids",
      name: "My Bids",
      component: MyBids,
      beforeEnter: guardMyroute,
    },
    {
      path: "/newlisting",
      name: "New Listing",
      component: NewListing,
      beforeEnter: guardMyroute,
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
      beforeEnter: guardMyroute,
    },
    {
      path: "/noresults",
      name: "No Results",
      component: NoResults,
      beforeEnter: guardMyroute,
    },
    {
      path: "/confirmtransaction",
      name: "Confirm Transaction",
      component: ConfirmTransaction,
      beforeEnter: handleTransaction,
    },
    {
      path: "/landing",
      name: "Landing",
      component: Landing,
    },
  ],
});

function guardMyroute(to, from, next) {
  auth.onAuthStateChanged(async (user) => {
    if (user === null) {
      next("/login");
    } else {
      next();
    }
  });
}

function handleTransaction(to, from, next) {
  auth.onAuthStateChanged(async (user) => {
    if (user === null) {
      next(`/login?listingID=${to.query.listingID}&data=${to.query.data}`);
    } else {
      next();
    }
  });
}

router.pushReload = async function (location) {
  await this.push(location);
  window.location.reload();
};

export default router;
